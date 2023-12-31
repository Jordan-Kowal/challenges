defmodule Mix.Tasks.Day6 do
  @moduledoc "Day 6"

  use AdventOfCode.DayTask

  @type race :: {integer(), integer()}

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    lines
    |> Enum.map(&parse_line_p1/1)
    |> Enum.zip()
    |> Enum.reduce(1, fn race, acc ->
      compute_winning_presses(race)
      |> Enum.count()
      |> Kernel.*(acc)
    end)
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    lines
    |> Enum.map(&parse_line_p2/1)
    |> List.to_tuple()
    |> compute_winning_presses()
    |> Enum.count()
  end

  @spec parse_line_p1(String.t()) :: [integer()]
  defp parse_line_p1(line) do
    line
    |> String.split(" ")
    |> Enum.filter(&(&1 != "" and not String.contains?(&1, ":")))
    |> Enum.map(&String.to_integer/1)
  end

  @spec parse_line_p2(String.t()) :: integer()
  defp parse_line_p2(line) do
    line
    |> String.split(" ")
    |> Enum.filter(&(&1 != "" and not String.contains?(&1, ":")))
    |> Enum.reduce("", fn x, acc -> acc <> x end)
    |> String.to_integer()
  end

  # Use quadratic equation to find the first and last point of the winning range
  @spec compute_winning_presses(race()) :: [integer()]
  defp compute_winning_presses({time, distance}) do
    discriminant = :math.sqrt(time * time - 4 * distance)

    first_point =
      case round((-time + discriminant) / -2) do
        x when x * (time - x) > distance -> x
        x -> x + 1
      end

    last_point =
      case round((-time - discriminant) / -2) do
        x when x * (time - x) > distance -> x
        x -> x - 1
      end

    Range.new(first_point, last_point)
  end
end
