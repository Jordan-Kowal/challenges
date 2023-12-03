defmodule Mix.Tasks.Day2 do
  @moduledoc "Day 2"

  use AdventOfCode.DayTask

  @type round_recap :: %{required(String.t()) => integer()}
  # %{"red" => 1, "green" => 2, "blue" => 4}

  @type game_recap :: [round_recap()]
  # [%{"red" => 1, "green" => 2}, %{"red" => 1, "green" => 2, "blue" => 4}]

  @type colors_recap :: %{required(String.t()) => [integer()]}
  # %{"red" => [1, 0, 7]}

  @max_cubes_per_color %{
    "red" => 12,
    "green" => 13,
    "blue" => 14
  }

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    lines
    |> Enum.map(&parse_line/1)
    |> Enum.filter(fn {_, color_count_per_round} ->
      bag_has_enough_cubes?(color_count_per_round)
    end)
    |> Enum.reduce(0, fn {id, _}, acc -> acc + id end)
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    lines
    |> Enum.filter(fn line -> line != "" end)
    |> Enum.map(&parse_line/1)
    |> Enum.map(fn {_, color_count_per_round} ->
      Enum.reduce(color_count_per_round, 1, fn {_, counts}, acc -> Enum.max(counts) * acc end)
    end)
    |> Enum.sum()
  end

  @spec parse_line(String.t()) :: {integer(), colors_recap()}
  defp parse_line(""), do: {0, %{}}

  defp parse_line(line) do
    [game_name, rounds_line] = String.split(line, ": ")
    [_, id] = String.split(game_name, " ")

    colors_recap =
      rounds_line
      |> parse_rounds()
      |> rounds_to_colors_recap()

    {String.to_integer(id), colors_recap}
  end

  @spec bag_has_enough_cubes?(colors_recap()) :: boolean()
  defp bag_has_enough_cubes?(colors_recap) do
    Enum.all?(colors_recap, fn {color, counts} ->
      Enum.max(counts) <= Map.get(@max_cubes_per_color, color)
    end)
  end

  @spec parse_rounds(String.t()) :: game_recap()
  defp parse_rounds(rounds_line) do
    rounds_line
    |> String.split("; ")
    |> Enum.map(fn action ->
      action
      |> String.split(", ")
      |> Enum.reduce(%{}, fn cube, acc ->
        [amount, color] = String.split(cube, " ")
        Map.put(acc, color, String.to_integer(amount))
      end)
    end)
  end

  @spec rounds_to_colors_recap(game_recap()) :: colors_recap()
  defp rounds_to_colors_recap(game_recap) do
    Enum.reduce(["red", "green", "blue"], %{}, fn color, acc ->
      row =
        Enum.reduce(game_recap, [], fn round_map, acc ->
          acc ++ [Map.get(round_map, color, 0)]
        end)

      Map.put(acc, color, row)
    end)
  end
end
