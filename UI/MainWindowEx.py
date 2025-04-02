from UI.MainWindow import Ui_MainWindow
from CrawlData.Crawl import Crawl
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import QComboBox, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap
from Connectors.Connector import Connector
from model.model import Model
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import time
from datetime import datetime

class MainWindowEx(Ui_MainWindow):
    def __init__(self):
        self.connector = Connector()
        self.model = Model()

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        self.lblLink.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_link.png"))
        self.lblLogo.setPixmap(QPixmap("/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/images/ic_agoda.png"))

        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(True)
        self.lblHotel.setFont(font)
        self.lblHotel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        font = QtGui.QFont()
        font.setBold(True)  # Chỉnh chữ thành đậm
        self.btnCrawl.setFont(font)
        self.btnBasic.setFont(font)
        self.btnDura.setFont(font)
        self.btnType.setFont(font)
        self.btnCoun.setFont(font)
        self.btnPieLabel.setFont(font)
        self.btnLineRate.setFont(font)
        self.btnHisRate.setFont(font)

        self.basic_labels = [self.lblB1, self.lblB2, self.lblB3, self.lblB4, self.lblB5, self.lblB6, self.lblB7, self.lblB8]

        self.btnCrawl.clicked.connect(self.processCrawl)

        self.connectDatabase()
        sql1 = 'SELECT CountryName FROM COUNTRY'
        self.countries = self.connector.queryData(sql1)['CountryName'].tolist()
        self.cboCusCoun.addItems(self.countries)
        countries_hotel = ['United States','Australia','Canada']
        self.cboHotelCoun.addItems(countries_hotel)

        sql2 = 'SELECT Distinct TripType FROM COMMENT'
        self.trips = self.connector.queryData(sql2)['TripType'].tolist()
        self.cboTripType.addItems(self.trips)

        self.tblCustomers.setColumnCount(3)
        self.tblCustomers.setHorizontalHeaderLabels(["Id", "Customer Name", "Customer Country"])
        self.tblCustomers.setColumnHidden(0, True)

        self.tblHotel.setColumnCount(6)
        self.tblHotel.setHorizontalHeaderLabels(["Id", "Hotel Name", "Hotel Country", "Hotel Address", "Hotel Rating", "Hotel Reviews"])
        self.tblHotel.setColumnHidden(0, True)

        # Handle RowClick
        self.tblCustomers.cellClicked.connect(self.load_data_from_customer)
        self.tblHotel.cellClicked.connect(self.load_data_from_hotel)
        self.tblCountry.cellClicked.connect(self.load_data_from_country)
        self.tblComments.cellClicked.connect(self.load_data_from_comment)

        self.btnLocCus.clicked.connect(self.locCustomers)
        self.btnLocHotel.clicked.connect(self.locHotels)
        self.btnLocCountry.clicked.connect(self.locCountry)
        self.btnLocComment.clicked.connect(self.locComments)
        self.btnHotelLuu.clicked.connect(self.save_hotel)
        self.btnCusLuu.clicked.connect(self.save_customer)
        self.btnHotelThem.clicked.connect(self.reset_hotel)
        self.btnCusThem.clicked.connect(self.reset_customer)
        self.btnHotelXoa.clicked.connect(self.delete_hotel)
        self.btnCusXoa.clicked.connect(self.delete_customer)
        self.btnHotelCapNhat.clicked.connect(self.update_hotel)
        self.btnCusCapNhat.clicked.connect(self.update_customer)

    def connectDatabase(self):
        self.connector.server = "localhost"
        self.connector.port = 3306
        self.connector.database = "KTLT"
        self.connector.username = "root"
        self.connector.password = ""
        self.connector.connect()

    def allowButton(self):
        self.btnBasic.clicked.connect(self.basic_statistics)
        self.btnHisRate.clicked.connect(self.rating_statistics)
        self.btnPieLabel.clicked.connect(self.rate_labels)
        self.btnLineRate.clicked.connect(self.rating_distribution_over_time)
        self.btnCoun.clicked.connect(self.count_by_country)
        self.btnType.clicked.connect(self.rate_by_room)
        self.btnDura.clicked.connect(self.duration_distribution)

    def processCrawl(self):
        self.lblHotel.setText("Loading...")
        self.openChrome()
        time.sleep(5)
        self.getHotelInfor()
        self.getReviewInfor()
        self.allowButton()

    def openChrome(self):
        link = self.txtLink.text()
        self.crawl = Crawl(link)
        self.crawl.openWeb()

    def getHotelInfor(self):
        self.hotel_name, hotel_address, hotel_country, hotel_rating = self.crawl.crawlHotelInfor()
        # self.connectDatabase()
        sql = "SELECT CountryID FROM COUNTRY WHERE CountryName = '%s'" % hotel_country
        self.hotel_country = self.connector.queryData(sql)['CountryID'].iloc[0]
        sql1 = "SELECT HotelName, CountryID FROM HOTEL WHERE HotelName = '%s'" % self.hotel_name
        res = self.connector.queryData(sql1)
        if res.empty:
            sql2 = ("INSERT INTO HOTEL(HotelName,HotelAddress,CountryID,HotelRating) "
                    "VALUES ('%s','%s','%s','%s')") % (self.hotel_name, hotel_address, self.hotel_country, hotel_rating)
            self.connector.queryData(sql2, fetch=False)
        else:
            sql3 = ("UPDATE HOTEL "
                    "SET HotelRating = '%s' where HotelName = '%s' and CountryID = '%s'") % (
                       hotel_rating, self.hotel_name, hotel_country)
            self.connector.queryData(sql3, fetch=False)
        self.lblHotel.setText(self.hotel_name)

    def getReviewInfor(self):
        pages = int(self.cboReviews.currentText()) // 5
        self.crawl.crawlReviewInfor(pages)
        df = pd.DataFrame(self.crawl.data)
        labels = self.model.dl_predict(df)
        for i, item in enumerate(self.crawl.data):
            sql4 = "SELECT CountryID FROM COUNTRY WHERE CountryName = '%s'" % item['customer_country']
            cus_country = self.connector.queryData(sql4)
            if cus_country is not None and not cus_country.empty:
                cus_country = cus_country['CountryID'].iloc[0]  # Lấy CountryID từ kết quả truy vấn
            else:
                cus_country = 251  # Hoặc một giá trị mặc định nếu không có kết quả
            sql5 = "SELECT * FROM CUSTOMER WHERE CustomerName = '%s' and CountryID = '%s'" % (
            item['customer_name'], cus_country)
            res = self.connector.queryData(sql5)
            if res.empty:
                # Thực hiện insert nếu không có kết quả
                sql6 = ("INSERT INTO CUSTOMER(CustomerName, CountryID) "
                        "VALUES ('%s','%s')") % (item['customer_name'], cus_country)
                self.connector.queryData(sql6, fetch=False)
            sql7 = "SELECT HotelID FROM HOTEL WHERE HotelName = '%s' and CountryID = '%s'" % (self.hotel_name, self.hotel_country)
            self.hotel_id = self.connector.queryData(sql7)
            if self.hotel_id is not None and not self.hotel_id.empty:
                self.hotel_id = self.hotel_id['HotelID'].iloc[0]
            sql8 = "SELECT CustomerID FROM CUSTOMER WHERE CustomerName = '%s' and CountryID = '%s'" % (
            item['customer_name'], cus_country)
            cus_id = self.connector.queryData(sql8)
            if cus_id is not None and not cus_id.empty:
                cus_id = cus_id['CustomerID'].iloc[0]
            else:
                cus_id = 1
            sql9 = "SELECT * FROM COMMENT WHERE CustomerID = '%s' and HotelID = '%s' and DateVisited = '%s'" % (cus_id,self.hotel_id, item['date_visited'])
            is_available = self.connector.queryData(sql9)
            if is_available.empty:
                sql10 = (
                           "INSERT INTO COMMENT(CustomerID,HotelID,ReviewRating,ReviewTitle,ReviewContent,DateVisited,DateReviewed,TripType,RoomType,Duration,Label) "
                           "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')") % (
                       cus_id, self.hotel_id, item['review_rating'] if item['review_rating'] != 'N/A' else 8.0,item['review_title'], item['review_content'], item['date_visited'], item['date_reviewed'],item['trip_type'], item['room_type'], item['duration'], labels[i][0])
                self.connector.queryData(sql10, fetch=False)

    def basic_statistics(self):
        self.hide_widgets()
        for label in self.basic_labels:
            self.layoutBasic.addWidget(label)
            label.setVisible(True)
        sql1 = "SELECT AVG(ReviewRating), AVG(Duration), COUNT(DISTINCT CustomerID), COUNT(*) FROM COMMENT WHERE HOTELID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(True)
        self.lblB1.setFont(font)
        self.lblB1.setStyleSheet("background-color: rgb(25, 78, 210); color: rgb(255, 255, 255);")
        self.lblB1.setText("Điểm đánh giá trung bình")
        self.lblB2.setText(str(df.iloc[0,0]))
        self.lblB3.setFont(font)
        self.lblB3.setStyleSheet("background-color: rgb(25, 78, 210); color: rgb(255, 255, 255);")
        self.lblB3.setText("Thời gian ở trung bình")
        self.lblB4.setText(str(df.iloc[0, 1]))
        self.lblB5.setFont(font)
        self.lblB5.setStyleSheet("background-color: rgb(25, 78, 210); color: rgb(255, 255, 255);")
        self.lblB5.setText("Số lượng khách hàng")
        self.lblB6.setText(str(df.iloc[0, 2]))
        self.lblB7.setFont(font)
        self.lblB7.setStyleSheet("background-color: rgb(25, 78, 210); color: rgb(255, 255, 255);")
        self.lblB7.setText("Số lượng bình luận")
        self.lblB8.setText(str(df.iloc[0, 3]))

    def hide_widgets(self):
        # Ẩn tất cả các widget trong layout
        for i in range(self.layoutBasic.count()):
            widget = self.layoutBasic.itemAt(i).widget()
            if widget:
                widget.setVisible(False)

    def show_widgets(self):
        # Hiện tất cả các widget trong layout
        for i in range(self.layoutBasic.count()):
            widget = self.layoutBasic.itemAt(i).widget()
            if widget:
                widget.setVisible(True)

    def rating_statistics(self):
        sql1 = "SELECT ReviewRating FROM COMMENT WHERE HOTELID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        df['ReviewRating'] = pd.to_numeric(df['ReviewRating'], errors='coerce')
        df = df.dropna(subset=['ReviewRating'])

        plt.figure(figsize=(8, 6))
        sns.histplot(df['ReviewRating'].dropna(), bins=5, kde=True, color="skyblue")
        plt.title("Phân bố điểm đánh giá")
        plt.xlabel("Rating")
        plt.ylabel("Số lượng")
        plt.xticks(range(1, 11))

        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure1.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure1.png'))

    def rate_labels(self):
        """2️ Biểu đồ tròn tỷ lệ đánh giá tích cực & tiêu cực"""
        sql1 = "SELECT Label FROM COMMENT WHERE HOTELID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        # Đảm bảo Label là kiểu số và thay thế 1 thành 'Good', 0 thành 'Bad'
        df['Label'] = pd.to_numeric(df['Label'], errors='coerce')
        df['Label'] = df['Label'].replace({1: 'Positive', 0: 'Negative'})

        # Tính số lượng các giá trị 'Good' và 'Bad'
        sentiment_counts = df['Label'].value_counts()

        # Vẽ biểu đồ tròn
        plt.figure(figsize=(6, 6))
        plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        plt.title("Tỷ lệ đánh giá tích cực và tiêu cực")
        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure2.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure2.png'))

    def rating_distribution_over_time(self):
        """3️ Biểu đồ xu hướng đánh giá theo thời gian"""
        sql1 = "SELECT DateVisited, ReviewRating FROM COMMENT WHERE HOTELID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        df['DateVisited'] = pd.to_datetime(df['DateVisited'])
        df['ReviewRating'] = pd.to_numeric(df['ReviewRating'], errors='coerce')
        # Nhóm dữ liệu theo ngày
        df = df.groupby('DateVisited')['ReviewRating'].mean().reset_index()

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=df['DateVisited'], y=df['ReviewRating'], marker="o", color="blue")
        # Vẽ biểu đồ
        plt.xticks(rotation=45)
        plt.title("Xu hướng điểm đánh giá theo thời gian")
        plt.xlabel("Ngày lưu trú")
        plt.ylabel("Trung bình Rating")
        plt.grid()
        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure3.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure3.png'))

    def count_by_country(self):
        """6️ Biểu đồ số lượng đánh giá theo quốc gia"""
        sql1 = (
                "SELECT CountryName, COUNT(DISTINCT c.CustomerID) AS Count FROM COMMENT c "
                "JOIN CUSTOMER c2 ON c.CustomerID = c2.CustomerID "
                "JOIN COUNTRY c3 on c2.CountryID = c3.CountryID "
                "WHERE HotelID = '%s' " 
                "GROUP BY CountryName "
                "ORDER BY Count DESC "
                "LIMIT 5 "
                ) % self.hotel_id
        df = self.connector.queryData(sql1)

        # Vẽ biểu đồ cột ngang
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Count', y='CountryName', data=df, palette="Set2", hue='CountryName')

        # Cài đặt các thuộc tính cho biểu đồ
        plt.title("Số lượng khách hàng theo quốc gia")
        plt.xlabel("Số lượng khách hàng")
        plt.ylabel("Quốc gia")
        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure4.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure4.png'))

    def rate_by_room(self):
        """Biểu đồ cột trung bình điểm đánh giá theo loại phòng"""
        sql1 = "SELECT RoomType, ReviewRating FROM COMMENT WHERE HotelID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        df = df.groupby('RoomType')['ReviewRating'].mean().reset_index()

        plt.figure(figsize=(12, 6))
        sns.barplot(x='ReviewRating', y='RoomType', data=df, hue='RoomType', palette="Blues_r", legend=False)
        plt.title("Điểm đánh giá trung bình theo loại phòng")
        plt.xlabel("Trung bình đánh giá")
        plt.ylabel("Loại phòng")
        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure5.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure5.png'))

    def duration_distribution(self):
        """4️ Biểu đồ Boxplot phân phối thời gian lưu trú"""
        sql1 = "SELECT Duration FROM COMMENT WHERE HotelID = '%s'" % self.hotel_id
        df = self.connector.queryData(sql1)
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')

        plt.figure(figsize=(6, 6))
        sns.boxplot(y=df['Duration'], color="lightblue")
        plt.title("Phân phối thời gian lưu trú")
        plt.ylabel("Số đêm lưu trú")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure6.png')
        self.hide_widgets()
        self.layoutBasic.addWidget(self.lblImage)
        self.lblImage.setVisible(True)
        self.lblImage.setPixmap(QPixmap('/Users/macbook/Documents/Uni/NĂM_3/HK6/KTLT/Project/Visualize/figure6.png'))

    def locCustomers(self):
        country = self.cboCusCoun.currentText()
        sql1 = ("SELECT CustomerID, CustomerName, CountryName FROM CUSTOMER c "
                "JOIN COUNTRY c2 ON c.CountryID = c2.CountryID "
                "WHERE c2.CountryName = '%s'") % country
        df = self.connector.queryData(sql1)
        if len(df) > 0:
            self.tblCustomers.setRowCount(len(df))
            for i in range(len(df)):
                self.tblCustomers.setItem(i, 0, QTableWidgetItem(str(df.iloc[i,0])))
                self.tblCustomers.setItem(i, 1, QTableWidgetItem(df.iloc[i,1]))
                self.tblCustomers.setItem(i, 2, QTableWidgetItem(df.iloc[i,2]))
        else:
            QMessageBox.information(self.MainWindow, "Notification", "No records found")

    def locHotels(self):
        country = self.cboHotelCoun.currentText()
        sql1 = ("SELECT HotelID, HotelName, CountryName, HotelAddress, HotelRating, HotelReviews "
                "FROM HOTEL h "
                "JOIN COUNTRY c ON h.CountryID = c.CountryID "
                "WHERE c.CountryName = '%s'") % country
        df = self.connector.queryData(sql1)
        if len(df) > 0:
            self.tblHotel.setRowCount(len(df))
            for i in range(len(df)):
                self.tblHotel.setItem(i, 0, QTableWidgetItem(str(df.iloc[i, 0])))
                self.tblHotel.setItem(i, 1, QTableWidgetItem(df.iloc[i, 1]))
                self.tblHotel.setItem(i, 2, QTableWidgetItem(df.iloc[i, 2]))
                self.tblHotel.setItem(i, 3, QTableWidgetItem(df.iloc[i, 3]))
                self.tblHotel.setItem(i, 4, QTableWidgetItem(str(df.iloc[i, 4])))
                self.tblHotel.setItem(i, 5, QTableWidgetItem(str(df.iloc[i, 5])))
        else:
            QMessageBox.information(self.MainWindow, "Notification", "No records found")

    def locCountry(self):
        sql1 = "SELECT CountryName, CountryCode FROM COUNTRY"
        df = self.connector.queryData(sql1)
        if len(df) > 0:
            self.tblCountry.setRowCount(len(df))
            for i in range(len(df)):
                self.tblCountry.setItem(i, 0, QTableWidgetItem(df.iloc[i, 0]))
                self.tblCountry.setItem(i, 1, QTableWidgetItem(df.iloc[i, 1]))
        else:
            QMessageBox.information(self.MainWindow, "Notification", "No records found")

    def convert_sqldate(self,date):
        date = datetime.strptime(date, '%d/%m/%Y')
        sql_date = date.strftime('%Y-%m-%d')
        return sql_date

    def locComments(self):
        trip = self.cboTripType.currentText()
        startdate = self.convert_sqldate(self.dEditStart.text())
        enddate = self.convert_sqldate(self.dEditEnd.text())
        sql1 = ("SELECT CustomerName, HotelName, ReviewRating, ReviewTitle, DateVisited, "
                "DateReviewed, RoomType, Duration, Label FROM COMMENT c "
                "JOIN Customer c2 ON c.CustomerID = c2.CustomerID "
                "JOIN Hotel h ON c.HotelID = h.HotelID "
                "WHERE c.TripType = '%s' AND DateVisited BETWEEN '%s' and '%s'") % (trip, startdate, enddate)
        df = self.connector.queryData(sql1)
        if len(df) > 0:
            self.tblComments.setRowCount(len(df))
            for i in range(len(df)):
                self.tblComments.setItem(i, 0, QTableWidgetItem(df.iloc[i, 0]))
                self.tblComments.setItem(i, 1, QTableWidgetItem(df.iloc[i, 1]))
                self.tblComments.setItem(i, 2, QTableWidgetItem(str(df.iloc[i, 2])))
                self.tblComments.setItem(i, 3, QTableWidgetItem(df.iloc[i, 3]))
                self.tblComments.setItem(i, 4, QTableWidgetItem(str(df.iloc[i, 4])))
                self.tblComments.setItem(i, 5, QTableWidgetItem(str(df.iloc[i, 5])))
                self.tblComments.setItem(i, 6, QTableWidgetItem(df.iloc[i, 6]))
                self.tblComments.setItem(i, 7, QTableWidgetItem(str(df.iloc[i, 7])))
                self.tblComments.setItem(i, 8, QTableWidgetItem(str(df.iloc[i, 8])))
        else:
            QMessageBox.information(self.MainWindow, "Notification", "No records found")

    def load_data_from_customer(self, row):
        self.cusselected_id = int(self.tblCustomers.item(row, 0).text())
        self.txtCusName.setText(self.tblCustomers.item(row, 1).text())
        self.txtCusCoun.setText(self.tblCustomers.item(row, 2).text())

    def load_data_from_hotel(self, row):
        self.hotelselected_id = int(self.tblHotel.item(row, 0).text())
        self.txtHotelName.setText(self.tblHotel.item(row, 1).text())
        self.txtHotelCountry.setText(self.tblHotel.item(row, 2).text())
        self.txtHotelAdd.setText(self.tblHotel.item(row, 3).text())
        self.dSpinHotelRa.setValue(float(self.tblHotel.item(row, 4).text()))
        self.spinHotelRe.setValue(int(self.tblHotel.item(row, 5).text()))

    def load_data_from_country(self, row):
        self.txtCountryName.setText(self.tblCountry.item(row, 0).text())
        self.txtCountryCode.setText(self.tblCountry.item(row, 1).text())

    def load_data_from_comment(self, row):
        self.txtCustomerName.setText(self.tblComments.item(row, 0).text())
        self.txtHotelName_2.setText(self.tblComments.item(row, 1).text())
        self.txtReviewRa.setText(str(self.tblComments.item(row, 2).text()))
        self.txtReviewTitle.setText(self.tblComments.item(row, 3).text())
        self.txtDateVisited.setText(self.tblComments.item(row, 4).text())
        self.txtDateReview.setText(self.tblComments.item(row, 5).text())
        self.txtRoom.setText(self.tblComments.item(row, 6).text())
        self.txtDur.setText(str(self.tblComments.item(row, 7).text()))
        self.txtLabel.setText(str(self.tblComments.item(row, 8).text()))

    def reset_customer(self):
        self.txtCusName.clear()
        self.txtCusCoun.clear()
        self.txtCusName.setFocus()

    def reset_hotel(self):
        self.txtHotelName.clear()
        self.txtHotelCountry.clear()
        self.txtHotelAdd.clear()
        self.dSpinHotelRa.clear()
        self.spinHotelRe.clear()
        self.txtHotelName.setFocus()

    def delete_customer(self):
        """Delete the selected customer from SQL and update the table."""
        if hasattr(self, 'cusselected_id') and self.cusselected_id:
            reply = QMessageBox.question(self.MainWindow, 'Delete Confirmation',
                                         "Are you sure you want to delete this row?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                sql1 = "DELETE FROM CUSTOMER WHERE CustomerID = '%s'" % self.cusselected_id
                self.connector.queryData(sql1, fetch=False)
                self.locCustomers()
                self.tblCustomers.setCurrentCell(-1, -1)  # Ensure no row is auto-selected
                self.reset_customer()
        else:
            QMessageBox.warning(self.MainWindow, "Warning", "Please select a row you want to delete.")

    def delete_hotel(self):
        """Delete the selected hotel from SQL and update the table."""
        if hasattr(self, 'hotelselected_id') and self.hotelselected_id:
            reply = QMessageBox.question(self.MainWindow, 'Delete Confirmation',
                                         "Are you sure you want to delete this row?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                sql1 = "DELETE FROM HOTEL WHERE HotelID = '%s'" % self.hotelselected_id
                self.connector.queryData(sql1, fetch=False)
                self.locHotels()
                self.tblHotel.setCurrentCell(-1, -1)  # Ensure no row is auto-selected
                self.reset_hotel()
        else:
            QMessageBox.warning(self.MainWindow, "Warning", "Please select a row you want to delete.")

    def update_customer(self):
        """Update selected customer details in SQL."""
        if hasattr(self, 'cusselected_id') and self.cusselected_id:
            new_name = self.txtCusName.text()
            sql1 = ("UPDATE CUSTOMER "
                    "SET CustomerName = '%s' "
                    "WHERE CustomerID = '%s'") % (new_name, self.cusselected_id)
            self.connector.queryData(sql1, fetch=False)
            self.locCustomers()
            self.reset_customer()
        else:
            QMessageBox.warning(self.MainWindow, "Warning", "Please select a row you want to update.")

    def update_hotel(self):
        """Update selected hotel details in SQL."""
        if hasattr(self, 'hotelselected_id') and self.hotelselected_id:
            new_name = self.txtCusName.text()
            new_add = self.txtHotelAdd.text()
            new_rating = self.dSpinHotelRa.value()
            new_review = self.spinHotelRe.value()
            sql1 = ("UPDATE HOTEL "
                    "SET HotelName = '%s',HotelAddress='%s',HotelRating='%s',HotelReviews = '%s' "
                    "WHERE HotelID = '%s'") % (new_name, new_add, new_rating, new_review, self.hotelselected_id)
            self.connector.queryData(sql1, fetch=False)
            self.locHotels()
            self.reset_hotel()
        else:
            QMessageBox.warning(self.MainWindow, "Warning", "Please select a row you want to update.")

    def save_customer(self):
        """Save selected customer details in SQL."""
        name = self.txtCusName.text().strip()
        country = self.txtCusCoun.text().strip()

        if name and country:
            sql1 = "SELECT CountryID FROM COUNTRY WHERE CountryName = '%s'" % country
            coun_id = self.connector.queryData(sql1)
            if coun_id is not None and not coun_id.empty:
                cus_country = coun_id['CountryID'].iloc[0]  # Lấy CountryID từ kết quả truy vấn
            else:
                cus_country = 251  # Hoặc một giá trị mặc định nếu không có kết quả
            sql2 = ("INSERT INTO CUSTOMER(CustomerName, CountryID)"
                    "VALUES ('%s', '%s')") % (name, cus_country)
            self.connector.queryData(sql2, fetch=False)
            self.locCustomers()
            self.reset_customer()
        else:
            QMessageBox.information(self.MainWindow, 'Notification',
                                    'Please enter the complete information.')

    def save_hotel(self):
        """Save selected hotel details in SQL."""
        name = self.txtCusName.text().strip()
        country = self.txtCusCoun.text().strip()
        add = self.txtHotelAdd.text().strip()
        rating = self.dSpinHotelRa.value()
        review = self.spinHotelRe.value()

        if name and country and add and rating and review:
            sql1 = "SELECT CountryID FROM COUNTRY WHERE CountryName = '%s'" % country
            coun_id = self.connector.queryData(sql1)
            if coun_id is not None and not coun_id.empty:
                cus_country = coun_id['CountryID'].iloc[0]  # Lấy CountryID từ kết quả truy vấn
            else:
                cus_country = 251  # Hoặc một giá trị mặc định nếu không có kết quả
            sql2 = ("INSERT INTO HOTEL(HotelName, CountryID, HotelAddress, HotelRating, HotelReviews)"
                    "VALUES ('%s', '%s','%s', '%s','%s')") % (name, country, add, rating, review)
            self.connector.queryData(sql2, fetch=False)
            self.locHotels()
            self.reset_hotel()
        else:
            QMessageBox.information(self.MainWindow, 'Notification',
                                    'Please enter the complete information.')

    def show(self):
        self.MainWindow.show()

    def close(self):
        self.MainWindow.close()