import time
from django.core.management.base import BaseCommand
from ai.services.vector_store import FaissVectorStore

class Command(BaseCommand):
    help = 'Indexes all NewsArticle records from the Django database into the FAISS vector store.'

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.NOTICE("Initiating FAISS vector database indexing pipeline..."))

        store = FaissVectorStore()
        indexed_count = store.rebuild_index_from_db()

        duration = round(time.time() - start_time, 2)
        self.stdout.write(self.style.SUCCESS(
            f"FAISS indexing complete in {duration}s: {indexed_count} articles vectorized and stored in index."
        ))
        self.stdout.write(self.style.NOTICE(f"Total vectors in FAISS index: {store.count()}"))
