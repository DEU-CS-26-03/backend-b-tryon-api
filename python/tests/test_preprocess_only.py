# python/tests/test_preprocess_only.py

from pathlib import Path
from vton.vton import preprocess_person, preprocess_cloth  # 예시

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "workspace" / "input"

def main():
    person = INPUT_DIR / "person.jpg"
    cloth  = INPUT_DIR / "garment.jpg"

    pid = preprocess_person(str(person))
    cid = preprocess_cloth(str(cloth))

    print("person_id:", pid)
    print("cloth_id :", cid)

if __name__ == "__main__":
    main()
