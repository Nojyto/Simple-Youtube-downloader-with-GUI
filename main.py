from datetime import datetime, timedelta
from threading import Thread
from multiprocessing.pool import ThreadPool
from pytube import YouTube, Playlist, exceptions, Search
from tkinter.messagebox import askyesno, showerror
import customtkinter as ctk
import moviepy.editor as mp
import eyed3
import os
import requests
import webbrowser
from PIL import Image
import io


class App(ctk.CTk):
    MAX_THREADS = 3
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.join(
        os.environ["USERPROFILE"]), "Downloads").replace("\\", "/")

    def __init__(self):
        super().__init__()

        # configure themes
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # configure window
        self.title("Youtube downloader")
        # self.iconbitmap('icon.ico')
        self.geometry(f"{800}x{600}")
        self.resizable(False, False)

        # configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # style variables
        options = {"padx": (10, 10), "pady": (10, 10), "sticky": "nsew"}
        btnStyle = {}

        # variables
        self.inputFileType = ctk.StringVar(value=".mp4")
        self.outputPath = ctk.StringVar(value=self.DEFAULT_OUTPUT_DIR)

        # bind enter to download
        self.bind("<Return>", lambda ev: self.threadDownload())

        # create logTextField
        self.logTextField = ctk.CTkTextbox(self, font=("Helvetica", 16))
        self.logTextField.grid(row=0, column=0, **options)
        self.appToTextField("Youtube downloader loaded.")

        # create main entry and buttons
        self.downloadBtn = ctk.CTkButton(
            master=self, fg_color="transparent", border_width=2, font=("Helvetica", 18), text="Download from url", command=self.threadDownload, height=75)
        self.downloadBtn.grid(row=1, column=0, **options)
        self.openFolderBtn = ctk.CTkButton(
            master=self, fg_color="transparent", border_width=2, font=("Helvetica", 18), text="Open folder", command=self.openOutputDir)
        self.openFolderBtn.grid(row=1, column=2, **options)

        # path window
        self.pathEntry = ctk.CTkEntry(
            self, textvariable=self.outputPath, state="disable")
        self.pathEntry.grid(row=2, column=0, columnspan=2, **options)
        self.setDirBtn = ctk.CTkButton(
            master=self, fg_color="transparent", border_width=2, text="Change dir", command=self.setOutputDir)
        self.setDirBtn.grid(row=2, column=2, **options)

        # create radiobuttons
        self.sideMenu = ctk.CTkFrame(self)
        self.sideMenu.grid(row=0, column=2, **options)

        self.sideMenuLabel = ctk.CTkLabel(
            master=self.sideMenu, text="Choose file type", font=("Helvetica", 16))
        self.sideMenuLabel.grid(
            row=0, column=0, columnspan=1, **options)

        self.sideMenuCategoryLabelVideo = ctk.CTkLabel(
            master=self.sideMenu, text="Video file types", font=("Helvetica", 12)).grid(
            row=1, column=0, columnspan=1, **options)

        self.radioBtnMp4 = ctk.CTkRadioButton(
            master=self.sideMenu, variable=self.inputFileType, value=".mp4", text=".mp4")
        self.radioBtnMp4.grid(row=2, column=0, **options)
        self.radioBtnWebm = ctk.CTkRadioButton(
            master=self.sideMenu, variable=self.inputFileType, value=".webm", text=".webm")
        self.radioBtnWebm.grid(row=3, column=0, **options)
        # self.radioBtnMov = ctk.CTkRadioButton(
        #     master=self.sideMenu, variable=self.inputFileType, value=".mov", text=".mov")
        # self.radioBtnMov.grid(row=4, column=0, **options)

        self.sideMenuCategoryLabelAudio = ctk.CTkLabel(
            master=self.sideMenu, text="Audio file types", font=("Helvetica", 12)).grid(
            row=5, column=0, columnspan=1, **options)

        self.radioBtn3 = ctk.CTkRadioButton(
            master=self.sideMenu, variable=self.inputFileType, value=".mp3", text=".mp3")
        self.radioBtn3.grid(row=6, column=0, **options)
        self.radioBtn4 = ctk.CTkRadioButton(
            master=self.sideMenu, variable=self.inputFileType, value=".wav", text=".wav")
        self.radioBtn4.grid(row=7, column=0, **options)

    def setOutputDir(self):
        newDir = ctk.filedialog.askdirectory(
            initialdir=self.outputPath.get(), title="Select a destination folder")
        if newDir != "":
            self.outputPath.set(newDir)

    def openOutputDir(self):
        os.startfile(self.outputPath.get())

    def appToTextField(self, line):
        curTime = datetime.now().strftime("[%H:%M]")

        self.logTextField.configure(state="normal")
        self.logTextField.insert(ctk.END, f"{curTime} {line}\n")
        self.logTextField.configure(state="disabled")

    def openPopup(self, query):
        def updateContents(s, direc=""):
            if direc == "right":
                updateContents.indx = min(
                    updateContents.indx + 1, updateContents.maxIndx)
            elif direc == "left":
                updateContents.indx = max(updateContents.indx - 1, 0)
            s = s[updateContents.indx]
            print(*dir(s), sep='\n')
            titleLabel.configure(text=f"{s.title}")
            summaryLabel.configure(
                text=f"Author: {s.author}   Views: {s.views:,}   Length: {timedelta(seconds=s.length)}")

            r = requests.get(s.thumbnail_url, allow_redirects=True)
            imgObj = ctk.CTkImage(Image.open(
                io.BytesIO(r.content)), size=(350, 166))
            img.configure(image=imgObj)
            img.bind("<Button-1>", lambda e: self.openUrl(s.watch_url))

            downloadBtn.configure(command=lambda: [Thread(
                target=self.downloadFile, args=(s.watch_url,)).start(), popup.destroy()])

        s = Search(query).results
        updateContents.indx = 0
        updateContents.maxIndx = len(s)

        popup = ctk.CTkToplevel(self)
        popup.title("Invalid url searching for video instead...")
        # self.iconbitmap('icon.ico')
        popup.geometry(f"{600}x{500}")
        popup.resizable(False, False)
        options = {"padx": (7, 7), "pady": (7, 7), "sticky": "nsew"}

        center = ctk.CTkFrame(popup, width=550, height=450)
        center.grid_propagate(False)
        center.grid(row=0, column=0, padx=25, pady=25)

        top = ctk.CTkFrame(center)
        titleLabel = ctk.CTkLabel(top, font=("Helvetica bold", 14))
        titleLabel.grid(row=2, column=0, columnspan=3, **options)
        summaryLabel = ctk.CTkLabel(top, font=("Helvetica", 12))
        summaryLabel.grid(row=3, column=0, columnspan=3, **options)

        img = ctk.CTkLabel(top, text="")
        img.grid(row=4, column=0, columnspan=3, **options)

        skipLeftBtn = ctk.CTkButton(
            master=top, fg_color="transparent", border_width=2, width=25, text="Back", command=lambda: updateContents(s, "left"))
        skipLeftBtn.grid(row=5, column=0, **options)
        downloadBtn = ctk.CTkButton(
            master=top, fg_color="transparent", border_width=2, width=25, text="Download")
        downloadBtn.grid(row=5, column=1, **options)
        skipRightBtn = ctk.CTkButton(
            master=top, fg_color="transparent", border_width=2, width=25, text="Next", command=lambda: updateContents(s, "right"))
        skipRightBtn.grid(row=5, column=2, **options)

        updateContents(s)
        top.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    @staticmethod
    def openUrl(url):
        webbrowser.open_new_tab(url)

    def threadDownload(self):
        try:
            link = self.clipboard_get()
        except:
            showerror("User error", "Error: empty clipboard!")

        if "list" in link:
            isWholeList = askyesno(title="Confirmation",
                                   message="Download whole playlist?")
            if isWholeList:
                Thread(target=self.downloadPlaylist, args=(link,)).start()
                return
        Thread(target=self.downloadFile, args=(link,)).start()

    def downloadPlaylist(self, link):
        p = Playlist(link)
        urls = p.video_urls
        listTitle = ""
        try:
            listTitle = p.title
        except:
            listTitle = "radioPlaylist"
        destFolder = os.path.join(self.outputPath.get(), listTitle)

        self.appToTextField(
            f"Starting download of playlist: {listTitle} ({len(urls)} videos)")

        if os.path.isdir(destFolder):
            overwriteFolder = askyesno(title="Confirmation",
                                       message="Folder already exists. Continue?")
            if not overwriteFolder:
                self.appToTextField("Download aborted")
                return
        else:
            os.mkdir(destFolder)

        self.outputPath.set(destFolder)
        with ThreadPool(processes=self.MAX_THREADS) as pool:
            pool.map(self.downloadFile, urls)

        self.appToTextField(f"Finished")

    def downloadFile(self, link):
        newFileExt = self.inputFileType.get()
        self.appToTextField(f"Start -> {link}")

        try:
            ytObj = YouTube(link)
            stream = ytObj.streams.get_highest_resolution()
            newFile = stream.download(output_path=self.outputPath.get())

            if newFileExt != '.mp4':
                newFilePath = os.path.splitext(newFile)[0] + newFileExt
                with mp.VideoFileClip(newFile) as videoObj:
                    match newFileExt:
                        case ".webm" | ".avi":
                            videoObj.write_videofile(
                                newFilePath, verbose=False, logger=None)
                        case ".mp3":
                            videoObj.audio.write_audiofile(
                                newFilePath, verbose=False, logger=None)

                            r = requests.get(ytObj.thumbnail_url,
                                             allow_redirects=True)
                            audioFile = eyed3.load(newFilePath)
                            audioFile.initTag()
                            audioFile.tag.images.set(
                                3, r.content, 'image/jpeg')
                            audioFile.tag.save()
                        case ".wav":
                            videoObj.audio.write_audiofile(newFilePath)
                        case _:
                            raise Exception("Unimplemented file type.")
                os.remove(newFile)

        except exceptions.RegexMatchError:
            self.appToTextField(f"Error -> invalid url")
            self.openPopup(link)
        except exceptions.VideoUnavailable:
            self.appToTextField(f"Error -> the video is not available")
        except exceptions.ExtractError:
            self.appToTextField(f"Error -> could not extract video")
        except Exception as e:
            self.appToTextField(f"Error -> {e}")
            #self.appToTextField(f"Error ({e.__class__.__name__}) -> {e}")
        else:
            self.appToTextField(f"Done -> {newFile}")


if __name__ == "__main__":
    app = App()
    app.mainloop()