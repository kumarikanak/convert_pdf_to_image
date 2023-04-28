import os
from pdf2image import convert_from_path
from PIL import Image
import json
from io import BytesIO
import urllib.request
import logging
import base64
import constants
import uuid
import time
from subprocess import check_output, CalledProcessError

# generate random uuid numbers
id = uuid.uuid4()
rand_num = id.int

# logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# same error_codes as dictionary
error_codes = constants.ERROR_CODES

def response_msg(status,payload):
    response = {"status": status, "payload": payload}
    return response
    
   
class ProcessAndConvertPdf:
    def __init__(self, photo_url):
        self.photo_url = photo_url
        self.pdf_name = None
        self.tmp_pdf = None
        self.response = None
        
    def convert_pdf_to_jpg(self):
        count_pages = self.get_pdf_pages_count()
        if(count_pages is not None):
            if(count_pages <= 3):
                converted_images = self.convert_pdf()
                image_name = "convereted_image"
                for i in range(0,len(converted_images)):
                    filename = image_name + "_" + str(i) + ".jpg"
                    converted_images[i].save(filename)
                self.response = response_msg("success",filename)
            else:
                # too many pages in the pdf 
                response_txt = error_codes["E416"]
                self.response = response_msg("failure",response_txt)
        else:
            # error while counting the pages using pdfinfo command
            response_txt = error_codes["E417"]
            self.response = response_msg("failure",response_txt)
        return self.response
    
    # get no. of pages in the pdf
    def get_pdf_pages_count(self):
        start_time = time.time()
        pdf_file = self.photo_url.split("/")[-1]
        self.pdf_name = pdf_file.split(".")[0]
        self.tmp_pdf = '/tmp/' + self.pdf_name + "_" + str(rand_num) + ".pdf"
        urllib.request.urlretrieve(self.photo_url, self.tmp_pdf)
        try:
            pdf_info_output = check_output(["pdfinfo", self.tmp_pdf]).decode()
            pages_line = [line for line in pdf_info_output.splitlines() if "Pages:" in line][0]
            num_pages = int(pages_line.split(":")[1])
            logger.info(f"Page_count in pdf: {num_pages}")
            logger.info("--- %s time taken to count pages in seconds ---" % (time.time() - start_time))
            return num_pages
        except CalledProcessError as sub_err:
            logger.error(f"Subprocess command error: {sub_err.output}")
            
    def convert_pdf(self):
        images = convert_from_path(self.tmp_pdf)
        logger.info("No. of pages in pdf: %s", str(len(images)))
        #File Size
        pdf_size = os.path.getsize(self.tmp_pdf)
        logger.info("Pdf Size is in kB: %s", str(pdf_size/1000))
        try:
            os.remove(self.tmp_pdf)
            logger.info("Temporary pdf removed")
        except:
            logger.info("No temporary pdf to remove")
        return images

		

ProcessAndConvertPdf("https://www.africau.edu/images/default/sample.pdf").convert_pdf_to_jpg()

