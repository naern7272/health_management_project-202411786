from modules.health_logic import HealthInfoManager


def main():

    # 건강정보 관리자 생성
    manager = HealthInfoManager()

    # 1. 건강정보 추가
    print("\n[1. 건강정보 추가]")

    manager.add_record("홍길동", 2000, "남", 175, 70)
    manager.add_record("김철수", 1998, "남", 180, 85)
    manager.add_record("이영희", 2002, "여", 165, 55)

    print("건강정보 3건 추가 완료")

    # 2. 전체 목록 조회
    print("\n[2. 전체 건강정보 조회]")

    for record in manager.get_all_records():
        print(record.to_dict())

    # 3. 상세 조회
    print("\n[3. 특정 건강정보 조회]")

    record = manager.get_record("P0001")

    if record:
        print(record.to_dict())
    else:
        print("정보가 없습니다.")

    # 4. 건강정보 수정
    print("\n[4. 건강정보 수정]")

    manager.update_record("P0001", weight=75)

    print(manager.get_record("P0001").to_dict())

    # 5. 건강정보 삭제
    print("\n[5. 건강정보 삭제]")

    manager.delete_record("P0002")

    for record in manager.get_all_records():
        print(record.to_dict())

    # 6. 통계 확인
    print("\n[6. 건강정보 통계]")

    stats = manager.get_statistics()

    for key, value in stats.items():
        print(f"{key}: {value}")

    # 7. 파일 저장
    print("\n[7. 파일 저장]")

    success, message = manager.save("json")
    print(message)

    # 8. 파일 불러오기
    print("\n[8. 파일 불러오기]")

    success, message = manager.load("json")
    print(message)

    # 9. 불러온 데이터 확인
    print("\n[9. 최종 데이터 확인]")

    for record in manager.get_all_records():
        print(record.to_dict())


if __name__ == "__main__":
    main()
