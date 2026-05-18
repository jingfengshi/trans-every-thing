import fitz
from .base import BaseProcessor, TextBlock

FALLBACK_FONT = "cjk"


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

        pages_blocks: dict[int, list[TextBlock]] = {}
        for block in blocks:
            pages_blocks.setdefault(block.page, []).append(block)

        for page_num, page_blocks in pages_blocks.items():
            page = doc[page_num]
            for block in page_blocks:
                rect = fitz.Rect(block.x, block.y, block.x + block.width, block.y + block.height)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                try:
                    page.insert_text(
                        (block.x, block.y + block.height * 0.8),
                        block.text,
                        fontsize=block.font_size,
                        color=self._int_to_rgb(block.metadata.get("color", 0)),
                    )
                except Exception:
                    page.insert_text(
                        (block.x, block.y + block.height * 0.8),
                        block.text,
                        fontname=FALLBACK_FONT,
                        fontsize=block.font_size,
                        color=self._int_to_rgb(block.metadata.get("color", 0)),
                    )

        doc.save(output_path)
        doc.close()

    @staticmethod
    def _int_to_rgb(color_int: int) -> tuple[float, float, float]:
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)
