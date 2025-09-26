# Velayne Strategy DSL Guide

## Пример DSL-стратегии

```yaml
name: 'my_strategy'
if: ALL[
  CROSSOVER(EMA(close, short=12), EMA(close, long=26)),
  RSI(close, period=14) < 70
]
then: BUY size=0.02 sl=ATR(14)*1.5 tp=ATR(14)*3
```

## Допустимые операции

- **Индикаторы:** EMA, SMA, RSI, ATR, HIGH(N), LOW(N), RET(N)
- **Комбинации:** CROSSOVER(a, b)
- **Логика:** AND/OR/NOT, сравнения > < >= <= == !=
- **ALL/ANY:** список условий (все/любое)
- **then:** BUY/SELL size, stop-loss, take-profit (арифметика только над разрешёнными функциями)

## Семантика

- Любая ветка if должна возвращать булево.
- then — словесное описание действия (поддерживаются только buy/sell/size/sl/tp).

## Ошибки DSL

- Неизвестная функция — "unknown func/op ..."
- Превышена глубина вложенности — "depth limit exceeded"
- Ошибка времени выполнения — "time limit exceeded"
- Некорректный YAML — "YAML syntax error"

## Советы

- Держите выражения короткими (до 3–4 уровней вложенности)
- Не используйте сложные формулы в then
- Проверяйте стратегию в Sandbox перед отправкой