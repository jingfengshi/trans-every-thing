import fitz
from pathlib import Path
from .base import BaseProcessor, TextBlock

# 系统 CJK 字体候选路径（Docker 容器内 + macOS）
_CJK_FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]


def _find_cjk_font() -> str | None:
    for p in _CJK_FONT_PATHS:
        if Path(p).exists():
            return p
    return None


class PDFProcessor(BaseProcessor):
    def extract_blocks(self, file_path: str) -> list[TextBlock]:
        blocks = []
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            for block in page.get_text("dict")["blocks"]:
                if block["type"] != 0:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        bbox = span["bbox"]
                        blocks.append(TextBlock(
                            text=text,
                            x=bbox[0],
                            y=bbox[1],
                            width=bbox[2] - bbox[0],
                            height=bbox[3] - bbox[1],
                            font_size=span["size"],
                            font_name=span["font"],
                            page=page_num,
                            metadata={
                                "color": span["color"],
                                "flags": span["flags"],
                                "origin": span["origin"],
                            }
                        ))
        doc.close()
        return blocks

    def rebuild(self, original_path: str, blocks: list[TextBlock], output_path: str) -> None:
        doc = fitz.open(original_path)
        cjk_font_path = _find_cjk_font()

        pages_blocks: dict[int, list[TextBlock]] = {}
        for block in blocks:
            pages_blocks.setdefault(block.page, []).append(block)

        for page_num, page_blocks in pages_blocks.items():
            page = doc[page_num]

            # Step 1: redact 删除所有原始文字区域（真正擦除，不只是覆盖）
            for block in page_blocks:
                # 稍微扩大 rect 确保完整覆盖
                rect = fitz.Rect(
                    block.x - 1,
                    block.y - 1,
                    block.x + block.width + 1,
                    block.y + block.height + 1,
                )
                page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

            # Step 2: 注册 CJK 字体
            font_name = "helv"
            if cjk_font_path:
                try:
                    page.insert_font(fontname="cjkfont", fontfile=cjk_font_path)
                    font_name = "cjkfont"
                except Exception:
                    pass

            # Step 3: 写入译文
            for block in page_blocks:
                rect = fitz.Rect(block.x, block.y, block.x + block.width, block.y + block.height)
                color = self._int_to_rgb(block.metadata.get("color", 0))
                # origin 是 baseline 坐标，直接用更准确
                origin = block.metadata.get("origin")
                if origin:
                    insert_pt = fitz.Point(origin[0], origin[1])
                else:
                    insert_pt = fitz.Point(block.x, block.y + block.height * 0.85)

                try:
                    page.insert_text(
                        insert_pt,
                        block.text,
                        fontname=font_name,
                        fontsize=block.font_size,
                        color=color,
                    )
                except Exception:
                    page.insert_textbox(
                        rect,
                        block.text,
                        fontname=font_name,
                        fontsize=max(block.font_size - 1, 6),
                        color=color,
                        align=0,
                    )

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()

    @staticmethod
    def _int_to_rgb(color_int: int) -> tuple[float, float, float]:
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)
