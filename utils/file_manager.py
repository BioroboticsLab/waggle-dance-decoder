#Bibliotheken die Importiert werden
import os
import shutil
import re
import csv
import sys

class File_manager:
    #Inital Path
    fm_start_path  = ""
    #Last visited Directory or path
    fm_last_dir   = ""
    #actual directoy
    fm_dir_path    = ""
    content     = []

    '''
    The Constructor of this Class
    '''
    def __init__(self, path):
        try:
            if (type(path) == str and os.path.isdir(path)):
                self.fm_dir_path   = path
                self.fm_start_path = os.getcwd()
        except Exception as e:
            raise

    '''
    Read a csv file and return it as dict
    '''
    def read_csv(self, path):
        content = {}

        with open(path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                content = row

        return content

    '''

    '''
    def search_files_in_dir(self, regex):
        tmp_files = []

        for f in os.listdir(self.fm_dir_path):
    		#Wenn der Dateiname mit dem oben Festgelegten Regulären Ausdrück übereinstimmt
            if regex.match(f):
    			#Wird er an die Liste angehängt
                tmp_files.append(f)

    	#Liste wird Absteigend sortiert. Also niedrigste Zeit zuerst
        tmp_files.sort()

        return tmp_files

    '''
    '''
    def search_in_content(self, regex, files):
        results = []

        for _file in files:
            if regex.search(i):
                results.append(f)

        return results

    '''
    '''
    def get_file_content_as_row(self, split):
        if (len(self.content) > 0):
            self.content = []

        data = open(dir_path ,"r")
        	#Zeilenweise wird die Datei gelesen
        for line in data:
    		#Hier wird die eingelesene Zeile nach jeden _ getrennt
    		#Beispiel dafür ist Cam_0_20160523113206_911960 wird zu
    		#Cam 0 20160523113206 911960
            tmp = line.split(split)

    		#Bastelt eine Zeichenkette aus den beiden Zeit angaben zusammen
            self.content.append(tmp[len(tmp-1)].rstrip('\n'))

    	#Hier wird die Datei wieder geschlossen
    	#Sollte immer gemacht werden, damit Fehlerquellen ausgeschlossen werden
        data.close()

    ''''
    Creates a new directoy.
    If the directory alredy exists it will do nothing.

    @param new_dir is the name of the new directory
    '''
    def create_new_dir(self, new_dir):
        #Dieser Teil fragt ab ob das der neue Ordner in dem Verzeichnis bereits Vorhaden ist oder nicht
        if not os.path.exists(new_dir):
        	#Wenn der Ordner noch nicht existiert wird er angelegt
            os.makedirs(new_dir)

        else:
            pass

    '''
    Copy a file from one directory to another

    @param file_to_copy the file that should be copied
    @param new_path     the path where the file should be copyed to
    @param new_filename the file renamed.
    '''
    def copy_to_new_dir(self, file_to_copy, new_path, new_filename = None):
        if (new_filename is None):
            new_filename = file_to_copy

        if not os.path.exists(new_path):
            shutil.copy(self.path + '/' + file_to_copy ,new_dir + '/' + new_filename)

        else:
            print("Unable to copy to Path file already exists")

    '''
    Change Directory like the cd command in the linux terminal

    @param new_dir the directory
    '''
    def change_dir(self, new_dir):
        try:
            if(os.path.isdir(new_dir)):
                self.last_dir = os.getcwd()
                os.chdir(new_dir)
                self.fm_dir_path = os.getcwd()

        except Exception as e:
            raise

    '''
    Returns the Structure of the directory
    e.g the Folder and Files in the actuell directoy
    '''
    def get_dir_structure(self):
        return os.listdir()

    '''
    Return to the start directory
    '''
    def return_to_start(self):
        self.fm_dir_path = self.fm_start_path
        os.chdir(self.fm_start_path)

    '''
    Set the Path directly

    @param new_path is the new Path
    '''
    def set_path(self, new_path):
        if(os.path.isdir(new_dir)):
            self.fm_last_dir   = self.fm_dir_path
            self.fm_dir_path   = new_path
        else:
            pass

    '''
    Returns the actual path
    '''
    def get_path(self):
        return self.fm_dir_path

    '''

    '''
    def get_content(self):
        return self.content
