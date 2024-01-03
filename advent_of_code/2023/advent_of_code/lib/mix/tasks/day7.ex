defmodule Mix.Tasks.Day7 do
  @moduledoc "Day 7"

  use AdventOfCode.DayTask

  @type hand :: [String.t()]
  @type hand_type ::
          :five_of_a_kind
          | :four_of_a_kind
          | :full_house
          | :three_of_a_kind
          | :two_pairs
          | :one_pair
          | :high_card
  @type bid :: integer()
  @type hand_data :: {hand(), bid(), hand_type()}

  @types %{
    five_of_a_kind: 6,
    four_of_a_kind: 5,
    full_house: 4,
    three_of_a_kind: 3,
    two_pairs: 2,
    one_pair: 1,
    high_card: 0
  }

  @impl AdventOfCode.DayTask
  def solve_p1(lines), do: solve(lines, false)

  @impl AdventOfCode.DayTask
  def solve_p2(lines), do: solve(lines, true)

  @spec solve([String.t()], boolean()) :: integer()
  defp solve(lines, jack_as_joker) do
    lines
    |> Enum.map(fn line -> parse_line(line, jack_as_joker) end)
    |> Enum.sort(fn cards1, cards2 -> compare_hands(cards1, cards2, jack_as_joker) end)
    |> Enum.reverse()
    |> Enum.with_index()
    |> Enum.map(fn {{_, bid, _}, index} -> (index + 1) * bid end)
    |> Enum.sum()
  end

  @spec parse_line(String.t(), boolean()) :: hand_data()
  defp parse_line(line, jack_as_joker) do
    [value, string_bid] = String.split(line, " ")
    hand = String.graphemes(value)
    {hand, String.to_integer(string_bid), compute_hand_type(hand, jack_as_joker)}
  end

  @spec compute_hand_type(hand(), boolean()) :: hand_type()
  defp compute_hand_type(hand, jack_as_joker) do
    jack_count = Enum.count(hand, &(&1 == "J"))

    hand
    |> Enum.frequencies()
    |> Map.values()
    |> Enum.sort()
    |> Enum.reverse()
    |> update_hand_count_with_jacks(jack_count, jack_as_joker)
    |> hand_type_from_card_count()
  end

  @spec update_hand_count_with_jacks(
          hand_count :: [integer()],
          jack_count :: integer(),
          jack_as_joker :: boolean()
        ) :: [integer()]
  defp update_hand_count_with_jacks(hand_count, _, false), do: hand_count

  defp update_hand_count_with_jacks(hand_count, 0, _), do: hand_count
  defp update_hand_count_with_jacks(hand_count, 5, _), do: hand_count

  defp update_hand_count_with_jacks(hand_count, jack_count, _) do
    [highest | rest] = List.delete(hand_count, jack_count)
    [highest + jack_count | rest]
  end

  @spec hand_type_from_card_count([integer()]) :: hand_type()
  defp hand_type_from_card_count([5]), do: :five_of_a_kind
  defp hand_type_from_card_count([4, 1]), do: :four_of_a_kind
  defp hand_type_from_card_count([3, 2]), do: :full_house
  defp hand_type_from_card_count([3 | _]), do: :three_of_a_kind
  defp hand_type_from_card_count([2, 2 | _]), do: :two_pairs
  defp hand_type_from_card_count([2 | _]), do: :one_pair
  defp hand_type_from_card_count([1 | _]), do: :high_card

  @spec compare_hands(hand_data(), hand_data(), boolean()) :: boolean()
  defp compare_hands({hand1, _, type1}, {hand2, _, type1}, jack_as_joker) do
    hand1
    |> Enum.zip(hand2)
    |> Enum.reduce_while(false, fn {card1, card2}, acc ->
      card1_value = card_to_value(card1, jack_as_joker)
      card2_value = card_to_value(card2, jack_as_joker)

      cond do
        card1_value > card2_value -> {:halt, true}
        card1_value < card2_value -> {:halt, false}
        true -> {:cont, acc}
      end
    end)
  end

  defp compare_hands({_, _, type1}, {_, _, type2}, _) do
    @types[type1] > @types[type2]
  end

  defp card_to_value(card, jack_as_joker) do
    case card do
      "A" -> 14
      "K" -> 13
      "Q" -> 12
      "J" -> if jack_as_joker, do: 1, else: 11
      "T" -> 10
      _ -> String.to_integer(card)
    end
  end
end
