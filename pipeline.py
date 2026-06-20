from crawler.crawler import get_html_then_cache
from organiser.organiser import organise
from writer.writer import write_section
from services.output_service import render
from pathlib import Path
import asyncio
import logging
from services.s3_service import upload_and_get_url

logging.basicConfig(
    level="INFO"
)
logger = logging.getLogger(__name__)

async def run_pipeline(url: str , package_name) -> str:
    #crawler agent
    crawled_pages = await get_html_then_cache(url)
    logger.info(f'Crawl process complete with {len(crawled_pages)} pages')

    #organiser agent
    sections_with_pages = organise(crawled_pages)
    if sections_with_pages is None:
        logger.error('Organiser agent failed to return a useable output')
        raise ValueError(f'Organise produced no useable content for {url}')
    
    #writer agent 
    written_sections = write_section(sections_with_pages)
    logger.info(f'Writing stage completed with {len(written_sections)} sections written')

    #render service
    path = render(written_sections, package_name)
    presigned_url = upload_and_get_url(path, package_name)
    logger.info(f'Pipeline run completed,\nall agents run successful\nPATH: {path}')
    return presigned_url


