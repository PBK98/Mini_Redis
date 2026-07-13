# Mini Redis

CLI 기반 Mini Redis 과제 구현입니다. 코드는 `mini_redis/` 디렉터리 아래에 있으며,
해시맵, 이중 연결 리스트, 최소 힙을 각각 별도 모듈로 분리했습니다.

## 파일 구조

- `mini_redis/linked_list.py`: LRU 추적에 사용하는 이중 연결 리스트
- `mini_redis/hash_map.py`: 체이닝 방식 해시맵
- `mini_redis/min_heap.py`: TTL 만료 관리를 위한 최소 힙
- `mini_redis/mini_redis.py`: Redis 명령 실행 로직과 메모리/LRU/TTL 관리
- `mini_redis/cli.py`: 명령어 파싱 및 REPL
- `mini_redis/__main__.py`: `python3 -m mini_redis` 실행 진입점
- `mini_redis/test_mini_redis.py`: 기본 동작 테스트

## 실행

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 -m mini_redis
```

종료는 `exit` 또는 `quit`를 입력하면 됩니다.

## 테스트

프로젝트 루트에서 다음 명령어를 실행합니다.

```bash
python3 -m unittest -v
```

## 지원 명령어

- `SET key value`
- `GET key`
- `DEL key`
- `EXISTS key`
- `DBSIZE`
- `KEYS`
- `CONFIG SET maxmemory bytes`
- `INFO memory`
- `EXPIRE key seconds`
- `TTL key`

## 구현 기준

- Python 3.8 이상에서 동작하도록 표준 라이브러리만 사용합니다.
- `dict`, `set`, `collections`로 핵심 저장소를 대체하지 않습니다.
- `HashMap`은 직접 설계한 해시 함수와 체이닝으로 충돌을 처리하며, 로드 팩터가 0.75를 초과하면 버킷을 2배 확장합니다.
- `DoublyLinkedList`는 `prev`, `next`, `data` 필드를 가진 노드로 LRU 순서를 O(1)에 갱신합니다.
- `MinHeap`은 `(expire_at, key)` 형태의 TTL 레코드를 저장하고, 오래된 TTL 레코드는 lazy deletion 방식으로 무시합니다.
- `used_memory`는 `len(utf8(key)) + len(utf8(value))`의 합으로 계산하며 자료구조 오버헤드는 제외합니다.
