"""生成各语言测试 PDF fixture。运行一次即可，生成文件提交到 git。"""
import fitz
from pathlib import Path

OUT = Path(__file__).parent


def _new_doc():
    doc = fitz.open()
    return doc, doc.new_page(width=595, height=842)


def make_en_simple():
    doc, page = _new_doc()
    page.insert_text((72, 80),  "Artificial Intelligence", fontsize=22, fontname="hebo")
    page.insert_text((72, 115), "A Brief Introduction",    fontsize=14, fontname="helv")
    page.draw_line((72, 130), (520, 130), color=(0.5, 0.5, 0.5))
    page.insert_text((72, 160), "Chapter 1: What is AI?",  fontsize=13, fontname="hebo")
    page.insert_text((72, 185), "Artificial Intelligence refers to the simulation of human", fontsize=11)
    page.insert_text((72, 200), "intelligence in machines programmed to think and learn.", fontsize=11)
    page.insert_text((72, 230), "Chapter 2: Machine Learning", fontsize=13, fontname="hebo")
    page.insert_text((72, 255), "Machine learning enables systems to learn from experience.", fontsize=11)
    page.insert_text((72, 270), "Key approaches include supervised and unsupervised learning.", fontsize=11)
    page.insert_text((72, 300), "Chapter 3: Applications",  fontsize=13, fontname="hebo")
    page.insert_text((72, 325), "AI is transforming healthcare, finance, and transportation.", fontsize=11)
    page.insert_text((72, 340), "Self-driving cars and medical diagnosis are key use cases.", fontsize=11)
    doc.save(str(OUT / "en_simple.pdf"))
    doc.close()


def make_zh_source():
    """中文源文档（需要 CJK 字体支持）"""
    import os
    cjk_candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    cjk_path = next((p for p in cjk_candidates if os.path.exists(p)), None)

    doc, page = _new_doc()
    if cjk_path:
        page.insert_font(fontname="cjk", fontfile=cjk_path)
        page.insert_text((72, 80),  "人工智能简介", fontname="cjk", fontsize=22)
        page.insert_text((72, 120), "第一章：什么是人工智能？", fontname="cjk", fontsize=13)
        page.insert_text((72, 145), "人工智能是指在机器中模拟人类智能的技术。", fontname="cjk", fontsize=11)
        page.insert_text((72, 165), "该术语由约翰·麦卡锡于1956年提出。", fontname="cjk", fontsize=11)
        page.insert_text((72, 195), "第二章：机器学习", fontname="cjk", fontsize=13)
        page.insert_text((72, 220), "机器学习使系统能够从经验中学习和改进。", fontname="cjk", fontsize=11)
    else:
        # fallback：用英文占位
        page.insert_text((72, 80),  "Chinese Source (font unavailable)", fontsize=16)
        page.insert_text((72, 120), "Artificial Intelligence Introduction", fontsize=11)
    doc.save(str(OUT / "zh_source.pdf"))
    doc.close()


def make_ja_source():
    import os
    cjk_candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    cjk_path = next((p for p in cjk_candidates if os.path.exists(p)), None)

    doc, page = _new_doc()
    if cjk_path:
        page.insert_font(fontname="cjk", fontfile=cjk_path)
        page.insert_text((72, 80),  "人工知能入門", fontname="cjk", fontsize=22)
        page.insert_text((72, 120), "第1章：人工知能とは？", fontname="cjk", fontsize=13)
        page.insert_text((72, 145), "人工知能とは、機械に人間の知能を模倣させる技術です。", fontname="cjk", fontsize=11)
        page.insert_text((72, 165), "この用語は1956年にジョン・マッカーシーが造りました。", fontname="cjk", fontsize=11)
        page.insert_text((72, 195), "第2章：機械学習", fontname="cjk", fontsize=13)
        page.insert_text((72, 220), "機械学習はシステムが経験から学習できるようにします。", fontname="cjk", fontsize=11)
    else:
        page.insert_text((72, 80),  "Japanese Source (font unavailable)", fontsize=16)
        page.insert_text((72, 120), "Artificial Intelligence Introduction in Japanese", fontsize=11)
    doc.save(str(OUT / "ja_source.pdf"))
    doc.close()


def make_mixed():
    """多字体、多字号混排"""
    doc, page = _new_doc()
    page.insert_text((72, 60),  "REPORT 2024",         fontsize=28, fontname="hebo", color=(0.1, 0.1, 0.5))
    page.insert_text((72, 100), "Executive Summary",   fontsize=16, fontname="hebo")
    page.draw_line((72, 112), (520, 112), color=(0.3, 0.3, 0.3), width=0.5)
    page.insert_text((72, 130), "This report covers key findings from our annual research.", fontsize=11)
    page.insert_text((72, 148), "Results show significant growth across all major markets.", fontsize=11)
    page.insert_text((72, 175), "Financial Highlights",  fontsize=14, fontname="hebo")
    page.insert_text((72, 198), "Revenue increased by 23% year-over-year.",  fontsize=11)
    page.insert_text((72, 214), "Operating margin improved to 18.5%.",        fontsize=11)
    page.insert_text((72, 230), "Cash reserves stand at $2.4 billion.",       fontsize=11)
    page.insert_text((72, 258), "Key Risks",            fontsize=14, fontname="hebo")
    page.insert_text((72, 280), "Market volatility remains a primary concern.", fontsize=10, color=(0.5, 0.1, 0.1))
    page.insert_text((72, 296), "Regulatory changes may impact Q3 outlook.",   fontsize=10, color=(0.5, 0.1, 0.1))
    page.insert_text((72, 780), "Confidential — Internal Use Only",            fontsize=8,  color=(0.6, 0.6, 0.6))
    doc.save(str(OUT / "mixed.pdf"))
    doc.close()


if __name__ == "__main__":
    make_en_simple()
    make_zh_source()
    make_ja_source()
    make_mixed()
    print("All test PDFs generated.")
