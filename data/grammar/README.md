## Grammar lessons content

Формат: один урок = один JSON-файл `grammar-XX.json` в этой папке.

Минимально обязательные поля:
- `id`, `title`, `title_id`, `order`, `difficulty`, `estimated_time`, `prerequisites`, `xp_reward`
- `theory.text`, `theory.key_points`
- `examples[]` (минимум 1)
- `exercises[]` (минимум 1)

Типы упражнений (на старте):
- `choice`: `question`, `options`, `correct`, `explanation?`
- `fill`: `question`, `answer`, `hint?`
- `translate`: `question`, `indonesian`, `accept[]?`, `explanation?`

### План (первые 20)

1. `grammar-01`: Приветствия и обращения
2. `grammar-02`: Личные местоимения (saya, kamu, dia...)
3. `grammar-03`: Простые предложения (SVO)
4. `grammar-04`: Вопросы (apa, siapa, di mana...)
5. `grammar-05`: Отрицание (tidak, bukan)
6. `grammar-06`: Базовые глаголы
7. `grammar-07`: Префикс me-
8. `grammar-08`: Префикс ber-
9. `grammar-09`: Суффикс -kan
10. `grammar-10`: Суффикс -i
11. `grammar-11`: Редупликация (мн. число)
12. `grammar-12`: Указательные (ini, itu)
13. `grammar-13`: Притяжательные
14. `grammar-14`: Числительные и счётные слова
15. `grammar-15`: Предлоги места (di, ke, dari)
16. `grammar-16`: Времена через контекст (sudah, sedang, akan)
17. `grammar-17`: Модальные (bisa, harus, mau)
18. `grammar-18`: Сравнения (lebih, paling, sama)
19. `grammar-19`: Пассив (di-)
20. `grammar-20`: Сложные предложения (yang, karena, tetapi)

