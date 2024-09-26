import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import cv2

class DatasetUploaderApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Smart Roll Call - Dataset Uploader Dashboard")
        self.window.geometry("600x500")

        # Define colors
        self.primary_color = "#4CAF50"
        self.secondary_color = "#FF5722"

        # Define fonts
        self.heading_font = ("Helvetica", 20, "bold")
        self.text_font = ("Helvetica", 12)

        # Heading Label
        self.heading_label = tk.Label(window, text="Smart Roll Call", font=self.heading_font, fg=self.primary_color)
        self.heading_label.pack(pady=20)

        # Upload Dataset Button
        self.upload_button = tk.Button(window, text="Upload Dataset", command=self.upload_dataset, bg=self.primary_color, fg="white", font=self.text_font)
        self.upload_button.pack(pady=10, padx=20, ipadx=10, ipady=5)

        # Capture Image Button
        self.capture_button = tk.Button(window, text="Capture Image", command=self.capture_image, bg=self.primary_color, fg="white", font=self.text_font)
        self.capture_button.pack(pady=10, padx=20, ipadx=10, ipady=5)

        # Upload Image Button
        self.upload_image_button = tk.Button(window, text="Upload Image", command=self.upload_image, bg=self.primary_color, fg="white", font=self.text_font)
        self.upload_image_button.pack(pady=10, padx=20, ipadx=10, ipady=5)

        # Dataset Label
        self.dataset_label = tk.Label(window, text="Uploaded Dataset will be displayed here", wraplength=500, font=self.text_font)
        self.dataset_label.pack(pady=10)

        # Generate CSV Button
        self.generate_csv_button = tk.Button(window, text="Generate CSV with Attendance", command=self.generate_csv, bg=self.primary_color, fg="white", font=self.text_font)
        self.generate_csv_button.pack(pady=10, padx=20, ipadx=10, ipady=5)

        # Generated CSV Label
        self.generated_csv_label = tk.Label(window, text="Generated CSV will be displayed here", wraplength=500, font=self.text_font)
        self.generated_csv_label.pack(pady=10)

        # Initialize dataset and temporary list
        self.dataset = []
        self.temp = []

    def upload_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile, fieldnames=['Name', 'Enrollment Id', 'Class', 'Image'])
                next(reader)
                dataset_text = "Uploaded Dataset:\n\n"
                for row in reader:
                    self.dataset.append(row)
                    dataset_text += f"Name: {row['Name']}, Enrollment Id: {row['Enrollment Id']}, Class: {row['Class']}, Image: {row['Image']}\n"
                self.dataset_label.config(text=dataset_text)

    def generate_csv(self):
        try:
            with open('attendance.csv', 'w', newline='') as csvfile:
                fieldnames = ['Name', 'Enrollment Id', 'Class', 'Image', 'Attendance']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for person in self.dataset:
                    name = person.get('Name', '')
                    if name in self.temp:
                        person['Attendance'] = 'Present'
                    else:
                        person['Attendance'] = 'Absent'
                    writer.writerow(person)
            print("Attendance CSV generated successfully.")
            self.read_generated_csv()
        except Exception as e:
            print("Error generating attendance CSV:", e)

    def read_generated_csv(self):
        try:
            with open('attendance.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                generated_csv_text = "Generated CSV file:\n\n"
                for row in reader:
                    name = row.get('Name', '')
                    roll_number = row.get('Enrollment Id', '')
                    class_name = row.get('Class', '')
                    image_path = row.get('Image', '')
                    attendance = row.get('Attendance', '')
                    generated_csv_text += f"Name: {name}, Enrollment Id: {roll_number}, Class: {class_name}, Image: {image_path}, Attendance: {attendance}\n"
            self.generated_csv_label.config(text=generated_csv_text)
            print("Generated CSV file read successfully.")
        except Exception as e:
            print("Error reading generated CSV file:", e)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if file_path:
            match_results = self.match_faces_in_image(file_path)
            print("Match results:", match_results)

    def match_faces_in_image(self, image_path):
        uploaded_image = cv2.imread(image_path)
        gray_uploaded_image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray_uploaded_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        match_results = []
        for (x, y, w, h) in faces:
            face = gray_uploaded_image[y:y+h, x:x+w]
            cv2.imwrite("uploaded_face.jpg", face)
            for person in self.dataset:
                match_result = self.match_face_with_captured_image("uploaded_face.jpg", person['Image'])
                print("Match result for", person['Name'], ":", match_result)
                if match_result == True:
                    print(person['Name'])
                    self.temp.append(person['Name'])
        print(self.temp)

    def match_face_with_captured_image(self, captured_image_path, dataset_image_path):
        captured_face = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
        resized_captured_face = cv2.resize(captured_face, (100, 100))
        dataset_image = cv2.imread(dataset_image_path, cv2.IMREAD_GRAYSCALE)
        resized_dataset_image = cv2.resize(dataset_image, (100, 100))
        similarity = cv2.compareHist(cv2.calcHist([resized_captured_face], [0], None, [256], [0, 256]),
                                      cv2.calcHist([resized_dataset_image], [0], None, [256], [0, 256]),
                                      cv2.HISTCMP_CORREL)
        print("Similarity with", dataset_image_path, ":", similarity)
        return similarity >= 0.80

    def capture_image(self):
        image_capture_app = ImageCaptureApp(self.dataset, self.temp)
        image_capture_app.run()

    def run(self):
        self.window.mainloop()

class ImageCaptureApp:
    def __init__(self, dataset, temp):
        self.window = tk.Toplevel()
        self.window.title("Smart Roll Call - Image Capture Dashboard")
        self.window.geometry("600x500")
        self.dataset = dataset
        self.temp = temp
        self.capture_button = tk.Button(self.window, text="Capture Image", command=self.capture_image, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.capture_button.pack(pady=10, padx=20, ipadx=10, ipady=5)
        self.image_label = tk.Label(self.window)
        self.image_label.pack()

        self.face_cap = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.video_cap = cv2.VideoCapture(0)

    def capture_image(self):
        ret, video_data = self.video_cap.read()
        col = cv2.cvtColor(video_data, cv2.COLOR_BGR2GRAY)
        faces = self.face_cap.detectMultiScale(
            col, 
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(video_data, (x, y), (x + w, y + h), (0, 255, 255), 1)
            face = video_data[y:y + h, x:x + w]
            cv2.imwrite(f"captured_face_{i}.jpg", face)
            pil_image = Image.fromarray(cv2.cvtColor(video_data, cv2.COLOR_BGR2RGB))
            tk_image = ImageTk.PhotoImage(image=pil_image)
            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image
            for person in self.dataset:
                match_result = self.match_face_with_captured_image(f"captured_face_{i}.jpg", person['Image'])
                print("Match result for", person['Name'], ":", match_result)
                if match_result:
                    self.temp.append(person['Name'])
        print(self.temp)

    def match_face_with_captured_image(self, captured_image_path, dataset_image_path):
        captured_face = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
        resized_captured_face = cv2.resize(captured_face, (100, 100))
        dataset_image = cv2.imread(dataset_image_path, cv2.IMREAD_GRAYSCALE)
        resized_dataset_image = cv2.resize(dataset_image, (100, 100))
        similarity = cv2.compareHist(cv2.calcHist([resized_captured_face], [0], None, [256], [0, 256]),
                                      cv2.calcHist([resized_dataset_image], [0], None, [256], [0, 256]),
                                      cv2.HISTCMP_CORREL)
        print("Similarity with", dataset_image_path, ":", similarity)
        return similarity >= 0.80

    def run(self):
        self.window.mainloop()

root = tk.Tk()
root.title("Smart Roll Call")
dataset_app = DatasetUploaderApp(root)
dataset_app.run()
