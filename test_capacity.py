from mini_redis.hash_map import HashMap


def main() -> None:
    h = HashMap()

    print("초기 상태")
    print("capacity:", h.capacity)
    print("size:", h.size())
    print()

    for i in range(7):
        key = "k" + str(i)
        before_capacity = h.capacity
        h.put(key, "v")
        resized = "resize 발생" if h.capacity != before_capacity else "resize 없음"
        print(
            key
            + " 추가 -> size: "
            + str(h.size())
            + ", capacity: "
            + str(h.capacity)
            + ", load_factor: "
            + str(h._load_factor())
            + " ("
            + resized
            + ")"
        )

    print()
    print("최종 상태")
    print("capacity:", h.capacity)
    print("size:", h.size())


if __name__ == "__main__":
    main()
