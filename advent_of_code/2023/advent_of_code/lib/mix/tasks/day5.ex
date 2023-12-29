defmodule Mix.Tasks.Day5 do
  @moduledoc "Day 5"

  use AdventOfCode.DayTask

  @type seed :: integer()

  @type map_key ::
          :seed_to_soil
          | :soil_to_fertilizer
          | :fertilizer_to_water
          | :water_to_light
          | :light_to_temperature
          | :temperature_to_humidity
          | :humidity_to_location

  @type map_values :: {destination :: integer(), source :: integer(), size :: integer()}
  @type maps :: %{map_key() => [map_values()]}

  @ordered_map_keys [
    :seed_to_soil,
    :soil_to_fertilizer,
    :fertilizer_to_water,
    :water_to_light,
    :light_to_temperature,
    :temperature_to_humidity,
    :humidity_to_location
  ]

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    {seeds, maps} = parse_lines(lines)

    seeds
    |> Enum.map(fn seed -> find_seed_location(seed, maps) end)
    |> Enum.min()
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    {seeds, maps} = parse_lines(lines)

    seeds
    |> Enum.chunk_every(2)
    |> Enum.map(fn [seed, length] ->
      recursive_find_seed_location(seed, length, maps)
    end)
    |> Enum.min()
  end

  @spec parse_lines([String.t()]) :: {[seed()], maps()}
  def parse_lines(lines) do
    lines = lines |> Enum.map(&String.trim/1) |> Enum.filter(&(&1 != ""))
    [first | rest] = lines
    seeds = extract_seeds_from_first_line(first)

    {maps, _} =
      Enum.reduce(rest, {%{}, nil}, fn line, {acc, key} ->
        if String.contains?(line, "map") do
          {acc, title_line_to_atom(line)}
        else
          numbers = String.split(line, " ") |> Enum.map(&String.to_integer/1) |> List.to_tuple()
          acc = Map.update(acc, key, [numbers], &(&1 ++ [numbers]))
          {acc, key}
        end
      end)

    {seeds, maps}
  end

  @spec extract_seeds_from_first_line(String.t()) :: [integer()]
  defp extract_seeds_from_first_line(input) do
    input
    |> String.split(": ")
    |> Enum.at(1)
    |> String.split(" ")
    |> Enum.map(&String.to_integer/1)
  end

  @spec title_line_to_atom(String.t()) :: atom()
  defp title_line_to_atom(line) do
    line
    |> String.split(" ")
    |> Enum.at(0)
    |> String.replace("-", "_")
    |> String.to_atom()
  end

  @spec find_seed_location(seed(), maps()) :: integer()
  defp recursive_find_seed_location(seed, 1, maps) do
    find_seed_location(seed, maps)
  end

  defp recursive_find_seed_location(seed, length, maps) do
    max = seed + length - 1
    step = Float.ceil(length / 2) |> trunc()
    start_dest = find_seed_location(seed, maps)
    middle_dest = find_seed_location(seed + step, maps)
    end_dest = find_seed_location(max, maps)

    # We assume loc(x) = y and loc(x + 1) = y + 1
    found_min =
      if start_dest + step != middle_dest do
        recursive_find_seed_location(seed, step, maps)
      else
        start_dest
      end

    if middle_dest + (max - step) != end_dest do
      result = recursive_find_seed_location(seed + step, length - step, maps)
      Enum.min([found_min, result])
    else
      found_min
    end
  end

  @spec find_seed_location(seed(), maps()) :: integer()
  defp find_seed_location(seed, maps) do
    Enum.reduce(@ordered_map_keys, seed, fn key, value ->
      compute_next_value(value, maps[key])
    end)
  end

  @spec compute_next_value(integer(), [map_values()]) :: integer()
  defp compute_next_value(value, map_values) do
    map_values
    |> Enum.find(fn {_, source, size} -> source <= value and value < source + size end)
    |> case do
      nil -> value
      {destination, source, _} -> destination + (value - source)
    end
  end
end
