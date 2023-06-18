import sys
from pathlib import Path
import uuid
import shutil
import os

from clean_folder.normalize import normalize

CATEGORIES = {
        'images': ['.JPEG', '.PNG', '.JPG', '.SVG'],
        'documents': ['.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX'],
        'audio': ['.MP3', '.OGG', '.WAV', '.AMR'],
        'video': ['.AVI', '.MP4', '.MOV', '.MKV'],
        'archives': ['.ZIP', '.GZ', '.TAR']
    }


def move_file(file: Path, root_dir: Path, categorie: str) -> None:
    target_dir = root_dir.joinpath(categorie)
    if not target_dir.exists():
        target_dir.mkdir()
    new_name = target_dir.joinpath(f"{normalize(file.stem)}{file.suffix}")
    if new_name.exists():
       new_name = new_name.with_name(f"{new_name.stem}-{uuid.uuid4()}{file.suffix}")
    file.rename(new_name)


def get_categories(file: Path) -> str:
    ext = file.suffix.upper()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "other"
 

def sort_folder(path: Path) -> None:
    
    category_files = {
        'images': [],
        'documents': [],
        'audio': [],
        'video': [],
        'archives': [],
        'other':[]
    }


    for item in path.glob("**/*"):
        if item.is_file():
                cat = get_categories(item)
                move_file(item, path, cat)
                category_files[cat].append(item.name)

    known_cat = [value for key, value in category_files.items() if key != 'other']
    known_cat = sum(known_cat, [])
    known_cat = [Path(value).suffix for value in known_cat]

    unknown_cat = [value for key, value in category_files.items() if key == 'other']
    unknown_cat = sum(unknown_cat, [])
    unknown_cat = [Path(value).suffix for value in unknown_cat]

    print('Files:')
    for key, value in category_files.items():
        if value:
            print(key, '; '.join(set(value)))

    print('Known category: ', ', '.join(set(known_cat)))
    print('Unknown category: ', ', '.join(set(unknown_cat)))
        

def delete_empty_folder(path: Path) -> None:
    
    folders_to_delete = [f for f in path.glob("**")]
    for folder in folders_to_delete[::-1]:
        if folder.is_dir() and not len(os.listdir(folder._str)):
            folder.rmdir() 


def unpack_archive(path: Path) -> None:
    
    for cat in CATEGORIES['archives']:
        for item in path.glob("**/*" + cat.lower()):
            if item.is_file():
                target_dir = Path(path.joinpath(Path(item).stem))
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                target_dir.mkdir()
                shutil.unpack_archive(item.as_posix(), target_dir.as_posix())


def main():

    try:
        path = Path(sys.argv[1])
    except IndexError:
        print("Must be 1 argument!")
        return
    
    if not path.exists():
        print(f'{path} not exist!')

    sort_folder(path) 
    unpack_archive(path.joinpath('archives'))
    delete_empty_folder(path)


if __name__ == '__main__':
    main()