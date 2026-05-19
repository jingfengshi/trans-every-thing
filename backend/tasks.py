import os
from pathlib import Path
from celery import Celery
from processors.factory import get_processor
from translator.factory import get_translator

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
UPLOAD_DIR = Path("/tmp/trans/uploads")
OUTPUT_DIR = Path("/tmp/trans/outputs")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(task_track_started=True)


@celery_app.task(bind=True)
def translate_file(self, task_id: str, file_path: str, engine: str, target_lang: str, style_prompt: str = ""):
    try:
        self.update_state(state="PROGRESS", meta={"progress": 0.1})

        processor = get_processor(file_path)
        blocks = processor.extract_blocks(file_path)

        self.update_state(state="PROGRESS", meta={"progress": 0.3})

        translator = get_translator(engine)
        texts = [b.text for b in blocks]

        batch_size = 50
        translated_texts = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            translated_texts.extend(translator.translate(batch, target_lang, style_prompt))
            progress = 0.3 + 0.6 * (i + batch_size) / max(len(texts), 1)
            self.update_state(state="PROGRESS", meta={"progress": min(progress, 0.9)})

        for block, translated in zip(blocks, translated_texts):
            block.text = translated

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ext = Path(file_path).suffix.lower()
        output_path = str(OUTPUT_DIR / f"{task_id}_translated{ext}")
        processor.rebuild(file_path, blocks, output_path)

        return {"output_path": output_path}

    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
