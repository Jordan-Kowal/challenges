# credo:disable-for-this-file Credo.Check.Refactor.Nesting
defmodule Mix.Tasks.Day3 do
  @moduledoc "Day 3"

  use AdventOfCode.DayTask

  @special_char_regex ~r/([^0-9.]){1}/
  @engine_regex ~r/(\*){1}/

  @type number_data :: %{
          row: integer(),
          start: integer(),
          end: integer(),
          value: integer()
        }

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    {numbers, char_positions} = parse_lines(lines, @special_char_regex)

    numbers
    |> Enum.filter(fn number ->
      adjacents = compute_adjacent_coordinates(number)
      not (MapSet.intersection(char_positions, adjacents) == MapSet.new())
    end)
    |> Enum.map(fn number -> number.value end)
    |> Enum.sum()
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    {numbers, engine_positions} = parse_lines(lines, @engine_regex)

    numbers
    |> Enum.reduce(%{}, fn number, acc ->
      adjacents = compute_adjacent_coordinates(number)
      points = MapSet.intersection(adjacents, engine_positions)
      count = MapSet.size(points)

      if count == 0 do
        acc
      else
        Enum.reduce(points, acc, fn coordinates, acc2 ->
          Map.update(acc2, coordinates, [number.value], fn list -> [number.value] ++ list end)
        end)
      end
    end)
    |> Enum.filter(fn {_, numbers} -> length(numbers) == 2 end)
    |> Enum.map(fn {_, [n1, n2]} -> n1 * n2 end)
    |> Enum.sum()
  end

  @spec parse_lines([String.t()], Regex.t()) :: {[number_data()], MapSet.t()}
  defp parse_lines(lines, special_char_regex) do
    lines
    |> Enum.with_index()
    |> Enum.reduce({[], MapSet.new()}, fn {line, index}, {acc_numbers, acc_chars} ->
      numbers = extract_numbers_from_line(index, line)
      chars = extract_special_characters_coordinates_from_line(index, line)
      {acc_numbers ++ numbers, MapSet.union(acc_chars, MapSet.new(chars))}
    end)
  end

  @spec extract_numbers_from_line(integer(), String.t()) :: [number_data()]
  defp extract_numbers_from_line(row_number, line) do
    values = Regex.scan(~r/(\d+)/, line)
    indexes = Regex.scan(~r/(\d+)/, line, return: :index)

    Enum.zip_with(values, indexes, fn [value, _], [{start, length}, _] ->
      %{
        row: row_number,
        start: start,
        end: start + length - 1,
        value: String.to_integer(value)
      }
    end)
  end

  @spec extract_special_characters_coordinates_from_line(integer(), String.t()) :: [
          {integer(), integer()}
        ]
  defp extract_special_characters_coordinates_from_line(row_number, line) do
    @special_char_regex
    |> Regex.scan(line, return: :index)
    |> Enum.map(fn [{index, _}, _] -> {row_number, index} end)
  end

  @spec compute_adjacent_coordinates(number_data()) :: MapSet.t()
  def compute_adjacent_coordinates(number) do
    length = number.end - number.start + 1

    MapSet.new(
      [
        {number.row, number.start - 1},
        {number.row, number.end + 1}
      ] ++
        Enum.map(0..(length + 1), fn i -> {number.row - 1, number.start + i - 1} end) ++
        Enum.map(0..(length + 1), fn i -> {number.row + 1, number.start + i - 1} end)
    )
  end
end
