import statistics

from modules.health_db import (
    HealthInfo,
    HealthInfoManager as BaseHealthInfoManager
)


class HealthInfoManager(BaseHealthInfoManager):
    
    # 1. 건강정보 추가 (CREATE)
    def add_record(self, name, birth_year, gender, height, weight):

        if not name.strip():
            raise ValueError("이름을 입력하세요.")

        height = float(height)
        weight = float(weight)

        if height <= 0 or weight <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")

        pid = self.next_id()

        record = HealthInfo(
            pid, name, birth_year, gender, height, weight
        )

        self.records.append(record)

        return record

    # 2. 건강정보 목록 조회 (READ)
    def get_all_records(self):

        return self.records

    # 3. 건강정보 상세 조회 (READ)
    def get_record(self, pid):

        for record in self.records:
            if record.id == pid:
                return record

        return None

    # 4. 건강정보 수정 (UPDATE)
    def update_record(self, pid, **kwargs):

        record = self.get_record(pid)

        if record is None:
            return False

        allowed_fields = [
            "name", "birth_year", "gender", "height", "weight"
        ]

        # 수정할 항목 검사 및 값 변환
        updates = {}

        for key, value in kwargs.items():

            if key not in allowed_fields:
                raise ValueError(f"잘못된 수정 항목: {key}")

            if key == "name":
                if not str(value).strip():
                    raise ValueError("이름을 입력하세요.")

            elif key == "birth_year":
                value = int(value)

            elif key in ("height", "weight"):
                value = float(value)

                if value <= 0:
                    raise ValueError("키와 몸무게는 0보다 커야 합니다.")

            updates[key] = value

        # 검증이 끝난 후 실제 데이터 수정
        for key, value in updates.items():
            setattr(record, key, value)

        # BMI 및 비만도 재계산
        record.recalc()

        return True

    # 5. 건강정보 삭제 (DELETE)
    def delete_record(self, pid):

        record = self.get_record(pid)

        if record is None:
            return False

        self.records.remove(record)

        return True

    # 6. 건강정보 통계 (STATISTICS)
    def get_statistics(self):

        if not self.records:
            return {"count": 0}

        heights = [r.height for r in self.records]
        weights = [r.weight for r in self.records]
        bmis = [r.bmi for r in self.records]

        total = len(self.records)

        # 평균 계산
        avg_height = statistics.mean(heights)
        avg_weight = statistics.mean(weights)
        avg_bmi = statistics.mean(bmis)

        # 모집단 표준편차 계산
        std_height = statistics.pstdev(heights)
        std_weight = statistics.pstdev(weights)
        std_bmi = statistics.pstdev(bmis)

        # 표본 표준편차 계산
        sample_std = {
            "height": statistics.stdev(heights) if total >= 2 else None,
            "weight": statistics.stdev(weights) if total >= 2 else None,
            "bmi": statistics.stdev(bmis) if total >= 2 else None
        }

        return {
            "count": total,

            "height": {
                "average": round(avg_height, 2),
                "std": round(std_height, 2),
                "min": min(heights),
                "max": max(heights)
            },

            "weight": {
                "average": round(avg_weight, 2),
                "std": round(std_weight, 2),
                "min": min(weights),
                "max": max(weights)
            },

            "bmi": {
                "average": round(avg_bmi, 2),
                "std": round(std_bmi, 2),
                "min": min(bmis),
                "max": max(bmis)
            },

            "sample_std": {
                key: round(value, 2) if value is not None else None
                for key, value in sample_std.items()
            }
        }


# 콘솔 APP 테스트
def console_app():

    manager = HealthInfoManager()

    while True:

        print("\n========== 건강정보 관리 프로그램 ==========")
        print("1. 건강정보 추가")
        print("2. 건강정보 목록 조회")
        print("3. 건강정보 상세 조회")
        print("4. 건강정보 수정")
        print("5. 건강정보 삭제")
        print("6. 건강정보 통계")
        print("7. 파일 저장")
        print("8. 파일 불러오기")
        print("0. 프로그램 종료")

        choice = input("메뉴 선택: ")

        try:

            # 1. 건강정보 추가
            if choice == "1":

                name = input("이름: ")
                birth_year = input("출생년도: ")
                gender = input("성별: ")
                height = input("키(cm): ")
                weight = input("몸무게(kg): ")

                record = manager.add_record(
                    name, birth_year, gender, height, weight
                )

                print("건강정보 추가 완료!")
                print(record.to_dict())

            # 2. 목록 조회
            elif choice == "2":

                records = manager.get_all_records()

                if not records:
                    print("등록된 건강정보가 없습니다.")

                for record in records:
                    print(record.to_dict())

            # 3. 상세 조회
            elif choice == "3":

                pid = input("조회할 ID: ")

                record = manager.get_record(pid)

                if record:
                    print("\n[건강정보 상세]")
                    for key, value in record.to_dict().items():
                        print(f"{key}: {value}")
                else:
                    print("해당 정보가 없습니다.")

            # 4. 건강정보 수정
            elif choice == "4":

                pid = input("수정할 ID: ")

                record = manager.get_record(pid)

                if not record:
                    print("해당 정보가 없습니다.")
                    continue

                print("수정 항목")
                print("1. 이름")
                print("2. 출생년도")
                print("3. 성별")
                print("4. 키")
                print("5. 몸무게")

                field = input("선택: ")

                fields = {
                    "1": "name",
                    "2": "birth_year",
                    "3": "gender",
                    "4": "height",
                    "5": "weight"
                }

                if field not in fields:
                    print("잘못된 선택입니다.")
                    continue

                value = input("새로운 값: ")

                result = manager.update_record(
                    pid, **{fields[field]: value}
                )

                if result:
                    print("수정 완료!")
                    print(record.to_dict())

            # 5. 건강정보 삭제
            elif choice == "5":

                pid = input("삭제할 ID: ")

                if manager.delete_record(pid):
                    print("삭제 완료!")
                else:
                    print("해당 정보가 없습니다.")

            # 6. 건강정보 통계
            elif choice == "6":

                stats = manager.get_statistics()

                print("\n========== 건강정보 통계 ==========")

                if stats["count"] == 0:
                    print("통계를 계산할 데이터가 없습니다.")
                    continue

                print(f"전체 레코드 수: {stats['count']}건")

                for field in ["height", "weight", "bmi"]:

                    info = stats[field]

                    print(f"\n[{field.upper()} 통계]")
                    print(f"평균: {info['average']}")
                    print(f"표준편차(모집단): {info['std']}")
                    print(f"최소값: {info['min']}")
                    print(f"최대값: {info['max']}")

                    sample = stats["sample_std"][field]
                    print(f"표준편차(표본): {sample}")

            # 7. 파일 저장
            elif choice == "7":

                fmt = input("저장 형식(json/csv/txt/pkl): ")

                success, message = manager.save(fmt)

                print(message)

            # 8. 파일 불러오기
            elif choice == "8":

                fmt = input("불러오기 형식(json/csv/txt/pkl): ")

                success, message = manager.load(fmt)

                print(message)

            # 0. 종료
            elif choice == "0":

                print("프로그램을 종료합니다.")
                break

            else:
                print("잘못된 메뉴 선택입니다.")

        except (ValueError, TypeError) as e:
            print("입력 오류:", e)


if __name__ == "__main__":
    console_app()
