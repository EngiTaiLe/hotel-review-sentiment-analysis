from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

class Crawl:
    def __init__(self, link):
        self.link = link
        self.driver = None
        self.data = []

    def get_text_safe(self, by, selector, element=None, default="N/A"):
        """Lấy nội dung text từ phần tử nếu có, nếu không trả về giá trị mặc định."""
        try:
            return (element or self.driver).find_element(by, selector).text.strip()
        except NoSuchElementException:
            return default

    def convert_date_reviewed(self, date):
        # Dictionary ánh xạ tên tháng sang số tháng
        months = {
            "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
            "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
        }

        # Tách ngày, tháng và năm
        month_name = date.split(', ')[0].split()[0]  # Lấy tên tháng
        day = date.split(', ')[0].split()[1]  # Lấy ngày
        year = date.split(', ')[1]  # Lấy năm

        # Chuyển tháng từ tên thành số
        month = months[month_name]

        # Đảm bảo ngày luôn có 2 chữ số
        day = day.zfill(2)

        # Định dạng lại theo định dạng MySQL 'YYYY-MM-DD'
        formatted_date = f"{year}-{month}-{day}"

        return formatted_date

    def convert_date_visited(self, date):
        # Dictionary ánh xạ tên tháng sang số tháng
        months = {
            "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
            "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
        }

        # Tách tháng và năm
        month_name = date.split()[0]  # Lấy tên tháng
        year = date.split()[1]  # Lấy năm

        # Chuyển tháng từ tên thành số
        month = months[month_name]

        # Sử dụng ngày 01 cho ngày đầu tháng
        day = "01"

        # Định dạng lại theo định dạng MySQL 'YYYY-MM-DD'
        formatted_date = f"{year}-{month}-{day}"

        return formatted_date

    def openWeb(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.link)

    def crawlHotelInfor(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-element-name="review-comment"]'))
        )
        hotel_name = self.get_text_safe(By.CSS_SELECTOR, 'h1.sc-jrAGrp.sc-kEjbxe.eDlaBj.gBJGnr')
        hotel_address = self.get_text_safe(By.CLASS_NAME, 'HeaderCerebrum__Address')
        hotel_country = next((c for c in ["United States", "Canada", "Australia"] if c in hotel_address), "N/A")
        hotel_address = hotel_address.replace(f", {hotel_country}",
                                              "").strip() if hotel_country != "N/A" else hotel_address
        hotel_rating = self.get_text_safe(By.CSS_SELECTOR, 'div.ReviewScore-Number.ReviewScore-Number--line-height')
        return hotel_name, hotel_address, hotel_country, hotel_rating

    def crawlReviewInfor(self, pages):
        for page in range(pages):
            print(f"Scraping page {page + 1}...")

            reviews = self.driver.find_elements(By.CSS_SELECTOR, "div.Review-comment")
            if not reviews:
                break  # Nếu không có đánh giá, dừng lại

            for review in reviews:
                # review_rating = self.get_text_safe(By.CSS_SELECTOR, 'div.Review-comment-leftHeader',review).split()[0]
                review_rating = self.get_text_safe(By.CSS_SELECTOR, 'span.sc-jrAGrp.sc-kEjbxe.fzPhrN.ehWyCi', review)
                customer_name = self.get_text_safe(By.TAG_NAME, "strong", review)
                customer_country = self.get_text_safe(By.CSS_SELECTOR, 'div.Review-comment-reviewer span:nth-of-type(2)', review)
                trip_type = self.get_text_safe(By.CSS_SELECTOR, 'div[data-info-type="group-name"] span', review)
                room_type = self.get_text_safe(By.CSS_SELECTOR, 'div[data-info-type="room-type"] span', review)
                date_visited_raw = self.get_text_safe(By.CSS_SELECTOR, 'div[data-info-type="stay-detail"] span', review)

                # Xử lý thời gian
                duration_match = re.search(r"(\d+)\snight", date_visited_raw)
                visit_match = re.search(r'in (\w+ \d{4})', date_visited_raw)

                review_title = self.get_text_safe(By.CSS_SELECTOR, "h4.sc-jrAGrp.sc-kEjbxe.lggFpR.doFXap", review).strip("“”'").replace("'", "\\'")
                review_content = self.get_text_safe(By.CSS_SELECTOR, "p.Review-comment-bodyText", review).replace("'", "\\'")
                date_reviewed = self.get_text_safe(By.CSS_SELECTOR, "span.sc-jrAGrp.sc-kEjbxe.eZGjuH.jiOEVL", review).split(
                    "Reviewed ")[-1]

                # Lưu dữ liệu
                # self.data["CustomerName"].append(customer_name)
                # self.data["CustomerCountry"].append(customer_country)
                # self.data["ReviewRating"].append(review_rating)
                # self.data["ReviewTitle"].append(review_title)
                # self.data["ReviewContent"].append(review_content)
                # self.data["DateVisited"].append(self.convert_date_visited(visit_match.group(1)) if visit_match else "N/A")
                # self.data["Duration"].append(duration_match.group(1) if duration_match else "N/A")
                # self.data["DateReview"].append(self.convert_date_reviewed(date_reviewed))
                # self.data["TripType"].append(trip_type)
                # self.data["RoomType"].append(room_type)
                self.data.append({"customer_name": customer_name,"customer_country": customer_country,"review_rating": review_rating,"review_title": review_title,"review_content": review_content,"date_visited": self.convert_date_visited(visit_match.group(1)), "duration": int(duration_match.group(1)), "date_reviewed": self.convert_date_reviewed(date_reviewed), "trip_type": trip_type, "room_type": room_type})

            # Chuyển trang tiếp theo nếu có
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-element-name="review-paginator-next"]'))
                )

                # Cuộn xuống để nút "Next" hiện ra
                self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)

                # Sử dụng JavaScript click nếu bị chặn
                self.driver.execute_script("arguments[0].click();", next_button)

                time.sleep(2)  # Giảm thời gian chờ
            except (NoSuchElementException, ElementClickInterceptedException):
                print("Không thể chuyển trang hoặc đã đến trang cuối.")
                break

# #%%
# from Connectors.Connector import Connector
#
# #%%
# connector = Connector()
# connector.server = "localhost"
# connector.port = 3306
# connector.database = "KTLT"
# connector.username = "root"
# connector.password = ""
# connector.connect()
#
#
#%%
# crawl = Crawl('https://www.agoda.com/orleans-hotel-and-casino/hotel/las-vegas-nv-us.html?countryId=181&finalPriceView=1&isShowMobileAppPrice=false&cid=1922896&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2025-03-12&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=USD&isFreeOccSearch=false&tag=428762ec-5187-4bca-a1d2-edfbd6779536&tspTypes=9&los=1&searchrequestid=7a2d68bc-9002-4d92-b18f-7a711b10af79&ds=Qbc9N8xaZAur5sQz')
#
# crawl.openWeb()
#
# #%%
# crawl.crawlReviewInfor(1)
#
# #%%
# import json
# with open('data/data.json', 'w', encoding='utf-8') as outfile:
#     json.dump(crawl.data, outfile, indent=4, ensure_ascii=False)

# #%%
# print(crawl.data[0]['review_rating'])