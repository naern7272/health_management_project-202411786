"""모듈 1: 데이터 구조화(레코드) 및 파일 I/O (JSON, CSV, TXT, Pickle)"""
import os
import json
import csv
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]
FILE_FORMATS = ["json", "csv", "txt", "pkl"]


def calc_bmi(height, weight):
    """BMI = 체중(kg) / (키(m))^2"""
    return round(weight / ((height / 100) ** 2), 2)


def classify_bmi(bmi):
    if bmi < 18.5:
        return "저체중"
    if bmi < 23:
        return "정상"
    if bmi < 25:
        return "과체중"
    if bmi < 30:
        return "1단계 비만"
    if bmi < 35:
        return "2단계 비만"
    return "3단계 비만"


class HealthInfo:
    """건강정보 레코드"""

    def __init__(self, pid, name, birth_year, gender, height, weight, bmi=None, status=None):
        self.id = pid
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = float(bmi) if bmi not in (None, "") else 0.0
        self.status = status or ""
        if not self.bmi or not self.status:
            self.recalc()

    def recalc(self):
        """키/몸무게 변경 시 BMI와 비만도 재계산"""
        self.bmi = calc_bmi(self.height, self.weight)
        self.status = classify_bmi(self.bmi)

    def to_dict(self):
        return {k: getattr(self, k) for k in FIELDS}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["name"], d["birth_year"], d["gender"],
                   d["height"], d["weight"], d.get("bmi"), d.get("status"))

    def __repr__(self):
        return f"HealthInfo({self.id}, {self.name}, {self.bmi}, {self.status})"


class HealthInfoManager:
    """건강정보관리자: 레코드 리스트 보관 + 파일 입출력"""

    def __init__(self, data_dir=DATA_DIR):
        self.records = []
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    # ---- 식별번호 ----
    def next_id(self):
        nums = [int(r.id[1:]) for r in self.records if r.id[1:].isdigit()]
        return f"P{max(nums, default=0) + 1:04d}"

    # ---- 파일 경로 ----
    def path(self, fmt):
        if fmt not in FILE_FORMATS:
            raise ValueError(f"지원하지 않는 형식: {fmt}")
        return os.path.join(self.data_dir, f"health_data.{fmt}")

    # ---- 저장 ----
    def save(self, fmt="json"):
        """반환: (성공여부, 메시지)"""
        try:
            p = self.path(fmt)
            rows = [r.to_dict() for r in self.records]
            if fmt == "json":
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)
            elif fmt == "csv":
                with open(p, "w", encoding="utf-8-sig", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=FIELDS)
                    w.writeheader()
                    w.writerows(rows)
            elif fmt == "txt":
                with open(p, "w", encoding="utf-8") as f:
                    f.write("\t".join(FIELDS) + "\n")
                    for r in rows:
                        f.write("\t".join(str(r[k]) for k in FIELDS) + "\n")
            elif fmt == "pkl":
                with open(p, "wb") as f:
                    pickle.dump(rows, f)
            return True, f"{os.path.basename(p)} 저장 완료 ({len(rows)}건)"
        except (OSError, ValueError, pickle.PickleError) as e:
            return False, f"저장 실패: {e}"

    # ---- 로드 ----
    def load(self, fmt="json"):
        """반환: (성공여부, 메시지). 실패 시 기존 데이터는 유지"""
        try:
            p = self.path(fmt)
            if fmt == "json":
                with open(p, "r", encoding="utf-8") as f:
                    rows = json.load(f)
            elif fmt == "csv":
                with open(p, "r", encoding="utf-8-sig", newline="") as f:
                    rows = list(csv.DictReader(f))
            elif fmt == "txt":
                with open(p, "r", encoding="utf-8") as f:
                    lines = [ln.rstrip("\n") for ln in f if ln.strip()]
                head = lines[0].split("\t")
                rows = [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]
            elif fmt == "pkl":
                with open(p, "rb") as f:
                    rows = pickle.load(f)
            loaded = [HealthInfo.from_dict(d) for d in rows]
            self.records = loaded
            return True, f"{os.path.basename(p)} 불러오기 완료 ({len(loaded)}건)"
        except FileNotFoundError:
            return False, f"파일이 없습니다: health_data.{fmt}"
        except (json.JSONDecodeError, pickle.UnpicklingError, KeyError,
                ValueError, IndexError, EOFError, TypeError) as e:
            return False, f"파일이 손상되었거나 형식이 올바르지 않습니다: {e}"
        except OSError as e:
            return False, f"파일 읽기 오류: {e}"