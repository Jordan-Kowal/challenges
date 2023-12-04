defmodule Mix.Tasks.Day4 do
  @moduledoc "Day 4"

  use AdventOfCode.DayTask

  @type card :: {integer(), MapSet.t(), MapSet.t()}
  @type card_copies :: %{integer() => integer()}

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    lines
    |> Enum.map(&parse_line/1)
    |> Enum.map(&card_to_points/1)
    |> Enum.sum()
    |> trunc()
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    cards = Enum.map(lines, &parse_line/1)
    {last_id, _, _} = Enum.at(cards, -1)

    cards
    |> Enum.reduce(%{}, fn {card_number, winning_numbers, player_numbers}, acc ->
      win_count = card_win_count({card_number, winning_numbers, player_numbers})
      acc = Map.update(acc, card_number, 1, &(&1 + 1))
      increment_card_copies(win_count, acc, card_number)
    end)
    |> Enum.filter(fn {k, _} -> k <= last_id end)
    |> Enum.reduce(0, fn {_, v}, acc -> acc + v end)
  end

  @spec parse_line(String.t()) :: [card()]
  defp parse_line(line) do
    # Line example: Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
    [card_name, numbers] = String.split(line, ": ")

    [_, card_number] =
      card_name
      |> String.split(" ")
      |> Enum.filter(&(&1 != ""))

    [winning_numbers, player_numbers] = String.split(numbers, " | ")

    {
      String.to_integer(card_number),
      parse_numbers(winning_numbers),
      parse_numbers(player_numbers)
    }
  end

  @spec parse_numbers(String.t()) :: MapSet.t()
  defp parse_numbers(numbers) do
    numbers
    |> String.split(" ")
    |> Enum.filter(&(&1 != ""))
    |> Enum.map(&String.to_integer/1)
    |> MapSet.new()
  end

  @spec card_win_count(card()) :: integer()
  defp card_win_count({_, winning_numbers, player_numbers}) do
    MapSet.size(MapSet.intersection(winning_numbers, player_numbers))
  end

  @spec increment_card_copies(integer(), card_copies(), integer()) :: card_copies()
  def increment_card_copies(0, card_copies, _card_number), do: card_copies

  def increment_card_copies(win_count, card_copies, card_number) when win_count > 0 do
    Enum.reduce(1..win_count, card_copies, fn i, acc ->
      multiplier = Map.get(acc, card_number, 1)
      Map.update(acc, card_number + i, multiplier, &(&1 + multiplier))
    end)
  end

  @spec card_to_points(card()) :: integer()
  defp card_to_points(card) do
    case card_win_count(card) do
      0 -> 0
      n -> :math.pow(2, n - 1)
    end
  end
end
