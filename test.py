# from vectordb.collection import get_collection

# collection = get_collection()

# print(collection.count())

from routers.resume import bulk_upload_resume

import asyncio
BULK_RESUME_PATH = r"/home/choice/Documents/archive/Resumes PDF/DevOps Engineer resumes"
if __name__ == "__main__":
    results = asyncio.run(
        bulk_upload_resume(BULK_RESUME_PATH)
    )
    print(results)