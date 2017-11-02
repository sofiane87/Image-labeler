import xlwt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os 
import sys
from PIL import Image



class labeler :

	def __init__(self):

		self.unique_labels = []
		self.taggedImgs = []
		self.tags = []
		self.comments = []
		self.remainingImgs = []
		self.save_path = None
		self.loaded_data = None
		self.data_path = None
		self.continue_labeling = True
		self.currentLabel = None

		self.run()

		self.currentID = None
		self.currentImg = None

	def load_data(self):
		if os.path.isdir(self.data_path):
			self.loaded_data = {}
			import numpy as np
			for filename in os.listdir(self.data_path):
				try:
					img = Image.open(os.path.join(self.data_path,filename))
					if img is not None:
						self.remainingImgs.append(filename)
						if len(np.array(img).shape) != 3:
							self.loaded_data[filename] = np.repeat(np.expand_dims(img,2),3,2)
						else:
							self.loaded_data[filename] = np.array(img)
				except:
					print('ignoring : {}'.format(filename))

		elif '.npy' in self.data_path :
			import numpy as np
			self.loaded_data = np.load(self.data_path)
			if len(self.loaded_data.shape) == 3:
				self.loaded_data = np.repeat(np.expand_dims(self.loaded_data,3),3,3)
			self.remainingimgs = list(range(self.loaded_data.shape[0]))
		else :
			QMessageBox.information(self.mainPage, "Empty Field",
									"This type of data is not handeled yet ! ")

	def load_previousWork(self):
		if os.path.exists(self.save_path):
			import pandas as pd
			df = pd.ExcelFile(self.save_path).parse("Sheet1")
			self.unique_labels = sorted(list(df.Label.unique()))
			self.taggedImgs = list(df.ID)
			self.tags = list(df.Label)
			self.comments = list(df.Comment)
			self.remainingImgs = [imgId for imgId in  self.remainingImgs if imgId not in self.taggedImgs]

					

	def normalize_savePath(self):
		if not(os.path.isfile(self.save_path)):
			if os.path.isdir(self.save_path):
				self.save_path = os.path.join(self.save_path,'saveFile.xls')


	def save_labels(self):
		book = xlwt.Workbook(encoding="utf-8")
		sheet1 = book.add_sheet("Sheet1")
		sheet1.write(0,0,"ID")
		sheet1.write(0,1,"Label")
		sheet1.write(0,2,"Comment")
		index = 1
		for ID, tag, comment in zip(self.taggedImgs, self.tags,self.comments):
			 sheet1.write(index,0,str(ID))
			 sheet1.write(index,1,str(tag))
			 sheet1.write(index,2,str(comment))
			 index += 1

		book.save(self.save_path)

	def label_img(self,idImg,tag,comment):
			
		self.taggedImgs.append(idImg)
		self.tags.append(tag)
		self.comments.append(comment)
		self.remainingImgs.remove(idImg)

	def buildLabelPage(self):
		self.labelPage = QWidget()


		### Dimensions
		self.labelPage.left = 10
		self.labelPage.top = 10
		self.labelPage.width = 640
		self.labelPage.height = 480


		self.labelPage.setWindowTitle('Labels')
		welcomeLabel = QLabel("Please Provide the labels to use separated with a comma")
		self.labelLine = QLineEdit()
		self.labelLine.setText(" , ".join(self.unique_labels))
		submitButton = QPushButton("&Submit")

		labelLayout = QGridLayout()
		labelLayout.addWidget(welcomeLabel, 0,0)
		labelLayout.addWidget(self.labelLine, 1, 0)
		labelLayout.addWidget(submitButton, 2, 0)


		self.labelPage.setLayout(labelLayout)
		submitButton.clicked.connect(self.parseLabels)
		self.labelPage.show()


	def parseLabels(self):
		self.unique_labels = list(set([word.strip().lower() for word in self.labelLine.text().split(',')]))
		if 'other' not in self.unique_labels :
			self.unique_labels.append('other')
		self.unique_labels	= sorted(self.unique_labels)

		self.BuildCoreWindow()


	def buildStartPage(self):
		self.mainPage = QWidget()
		self.mainPage.setWindowTitle('Welcome to Labeler')


		### Dimensions
		self.mainPage.left = 10
		self.mainPage.top = 10
		self.mainPage.width = 640
		self.mainPage.height = 480


		### Adding the elements 

		welcomeLabel = QLabel("Hi there ! Let's get started ...")

		nameLabel = QLabel("Input File/Folder : ")
		self.nameLine = QLineEdit()
		saveLabel = QLabel("Save Path : ")
		saveFileNameLabel = QLabel("Save Path : ")
		self.saveFilePathLine = QLineEdit()
		self.saveFileNameLine = QLineEdit()

		savePath, saveFileName = os.path.split(os.path.abspath(__file__))
		
		self.saveFilePathLine.setText(os.path.join(savePath,'saveFolder'))
		self.saveFileNameLine.setText('saveFile.xls')
		
		submitButton = QPushButton("&Submit")
		folderButton = QPushButton("&look for path")
		saveFolderButton = QPushButton("&look for path")

		def changeTitle(state):
			if state == Qt.Checked:
				self.continue_labeling = True
			else:
				self.continue_labeling = False

		
		self.cb = QCheckBox('Continue Previous Work', self.mainPage)
		self.cb.toggle()
		self.cb.stateChanged.connect(changeTitle)


		#### Designing the layout

		# buttonLayout1 = QVBoxLayout()
		# buttonLayout1.addWidget(nameLabel)
		# buttonLayout1.addWidget(folderButton)
		# buttonLayout1.addWidget(nameLine)
		# buttonLayout1.addWidget(submitButton)

		#### Defining the layout

		mainLayout = QGridLayout()
		mainLayout.addWidget(welcomeLabel, 0,1)
		mainLayout.addWidget(nameLabel, 1, 0)
		mainLayout.addWidget(self.nameLine, 1, 1)
		mainLayout.addWidget(folderButton, 1, 2)
		mainLayout.addWidget(saveLabel, 2, 0)
		mainLayout.addWidget(self.saveFilePathLine, 2, 1)
		mainLayout.addWidget(saveFolderButton, 2, 2)
		mainLayout.addWidget(saveFileNameLabel, 3, 0)
		mainLayout.addWidget(self.saveFileNameLine, 3, 1)
		mainLayout.addWidget(self.cb, 4, 0)
		mainLayout.addWidget(submitButton, 4, 2)

		self.mainPage.setLayout(mainLayout)

		folderButton.clicked.connect(self.openInputFileNameDialog)
		saveFolderButton.clicked.connect(self.openSaveFileNameDialog)
		submitButton.clicked.connect(self.submitPaths)


		#####

		self.mainPage.show()

	def openInputFileNameDialog(self):

		self.fileWindow = QFileDialog()
		self.fileWindow.setOption(self.fileWindow.DontUseNativeDialog, True)
		self.fileWindow.setFileMode(self.fileWindow.ExistingFiles)
		self.fileWindow.show()
		self.fileWindow.tree = self.fileWindow.findChild(QTreeView)

		def openClicked():
			inds = self.fileWindow.tree.selectionModel().selectedIndexes()
			files = []
			for i in inds:
				if i.column() == 0:
					files.append(os.path.join(str(self.fileWindow.directory().absolutePath()),str(i.data())))
			self.fileWindow.selectedFiles = files[0]
			if self.fileWindow.selectedFiles:
				 self.nameLine.setText(self.fileWindow.selectedFiles)
			self.fileWindow.hide()

		btns = self.fileWindow.findChildren(QPushButton)
		
		self.fileWindow.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
		self.fileWindow.openBtn.clicked.disconnect()
		self.fileWindow.openBtn.clicked.connect(openClicked)

	def openSaveFileNameDialog(self):

		
		self.fileWindow = QFileDialog()
		self.fileWindow.setOption(self.fileWindow.DontUseNativeDialog, True)
		self.fileWindow.setFileMode(self.fileWindow.ExistingFiles)
		self.fileWindow.show()
		self.fileWindow.tree = self.fileWindow.findChild(QTreeView)

		def openClicked():
			inds = self.fileWindow.tree.selectionModel().selectedIndexes()
			files = []
			for i in inds:
				if i.column() == 0:
					files.append(os.path.join(str(self.fileWindow.directory().absolutePath()),str(i.data())))
			self.fileWindow.selectedFiles = files[0]
			if self.fileWindow.selectedFiles:
				if os.path.isdir(self.fileWindow.selectedFiles):
					self.saveFilePathLine.setText(self.fileWindow.selectedFiles)
				else:
					savePath, saveFileName = os.path.split(self.fileWindow.selectedFiles)
					if savePath:
						self.saveFilePathLine.setText(savePath)

					if saveFileName != '' and saveFileName != '':
						self.saveFileNameLine.setText(saveFileName)
					else:
						self.saveFileNameLine.setText('saveFile.xls')

			self.fileWindow.hide()

		btns = self.fileWindow.findChildren(QPushButton)
		
		self.fileWindow.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
		self.fileWindow.openBtn.clicked.disconnect()
		self.fileWindow.openBtn.clicked.connect(openClicked)


	def run(self):
		app = QApplication(sys.argv)
		self.buildStartPage()
		sys.exit(app.exec_())


	def submitPaths(self):
		inputPath = self.nameLine.text()
		savePath = os.path.join(self.saveFilePathLine.text(),self.saveFileNameLine.text())

		if inputPath == "" or savePath == "":
			QMessageBox.information(self.mainPage, "Empty Field",
									"Please enter both an input path and a save path.")
		else:
			self.data_path = inputPath
			self.save_path = savePath
			self.normalize_savePath()
			self.load_data()
			if self.continue_labeling:
				self.load_previousWork()

			self.mainPage.hide()
			self.buildLabelPage()

	def BuildCoreWindow(self):

		self.labelPage.hide()
		
		self.corePage = QWidget()
		self.corePage.setWindowTitle("Let's Start !")

		### Dimensions
		self.corePage.left = 10
		self.corePage.top = 10
		self.corePage.width = 640
		self.corePage.height = 480

				### Adding the elements 

		welcomeLabel = QLabel("Hi there ! Let's get started ...")

		self.imageNameLabel = QLabel("Image ID : ")
		self.commentLabel = QLabel("Comment : ")
		self.commentInput = QLineEdit()

		self.togglebuttons = [QPushButton(str(label),self.corePage) for label in self.unique_labels]
		
		def setLabel(pressed):
			source = self.corePage.sender()
			if pressed:
				self.currentLabel = source.text()
				for button in self.togglebuttons:
					if button.text() != self.currentLabel:
						button.setChecked(False)

		hbox = QHBoxLayout()

		for button in self.togglebuttons:
			button.setCheckable(True)
			button.clicked[bool].connect(setLabel)
			hbox.addWidget(button)


		submitButton = QPushButton("&Confirm")
		backButton = QPushButton("&Previous")
		saveButton = QPushButton("&Save")

		submitButton.clicked.connect(self.NextImage)
		saveButton.clicked.connect(self.save_labels)
		backButton.clicked.connect(self.previousImage)
		### Image Handeling 
		self.pic = QLabel(self.corePage)

		self.updateImage()

		hbox2 = QHBoxLayout()
		hbox2.addWidget(backButton)
		hbox2.addWidget(saveButton)
		hbox2.addWidget(submitButton)

		hbox3 = QHBoxLayout()
		hbox3.addWidget(self.commentLabel)
		hbox3.addWidget(self.commentInput)

		coreLayout = QGridLayout()
		coreLayout.addWidget(self.imageNameLabel, 0, 0)
		coreLayout.addWidget(self.pic, 1, 0)
		coreLayout.addLayout(hbox, 2, 0)
		coreLayout.addLayout(hbox3, 3, 0)
		coreLayout.addLayout(hbox2, 4, 0)

		self.corePage.setLayout(coreLayout)
		self.corePage.show()

	def previousImage(self):
		if len(self.taggedImgs) == 0:
			QMessageBox.information(self.corePage, "Empty Field",
									"No Previous Image is available ! sorry !")
		else:
			

			self.currentID = self.taggedImgs[-1]
			self.taggedImgs = self.taggedImgs[:-1]
			self.remainingImgs = [self.currentID] + self.remainingImgs

			self.currentLabel = self.tags[-1]
			self.tags = self.tags[:-1]
			
			self.currentComment = self.comments[-1]
			self.comments = self.comments[:-1]

			self.updateImage()

			self.commentInput.setText(str(self.currentComment))
			for button in self.togglebuttons:
				if button.text() == self.currentLabel:
					button.setChecked(True)
				else:
					button.setChecked(False)


	def NextImage(self):
		if self.currentLabel == None:
			QMessageBox.information(self.corePage, "Empty Field",
									"Please select a tag !")
		else:
			self.currentComment = self.commentInput.text()
			self.label_img(self.currentID,self.currentLabel,self.currentComment)

			self.currentComment = None
			self.currentID = None
			self.currentLabel = None

			for button in self.togglebuttons:
				button.setChecked(False)
			self.commentInput.setText("")
			self.save_labels()
			if len(self.remainingImgs) != 0:
				self.updateImage()
			else: 
				QMessageBox.information(self.corePage, "Well Done !",
									"All images have been labelled and are saved in : \n{}".format(self.data_path))


	def updateImage(self):
		
		import numpy as np

		### Loading the Data 

		self.currentID = self.remainingImgs[0]
		self.currentImg = self.loaded_data[self.currentID].astype(np.uint32)

		self.flattendCurrentImg = (255 << 24 | self.currentImg[:,:,0] << 16 | self.currentImg[:,:,1] << 8 | self.currentImg[:,:,2])
		self.imageNameLabel.setText("Image ID : {}".format(self.currentID))

		qimage = QImage(self.flattendCurrentImg, self.currentImg.shape[0],self.currentImg.shape[1],QImage.Format_RGB32)
		pix = QPixmap(qimage)
		pix = pix.scaled(400, 400, Qt.KeepAspectRatio)
		self.pic.setPixmap(pix)
		self.pic.setAlignment(Qt.AlignCenter)


if __name__ == '__main__':
	labeler()



