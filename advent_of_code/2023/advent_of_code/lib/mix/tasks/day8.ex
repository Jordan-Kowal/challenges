defmodule Mix.Tasks.Day8 do
  @moduledoc "Day 8"

  use AdventOfCode.DayTask

  @type turn :: :L | :R
  @type direction_map :: %{String.t() => {String.t(), String.t()}}

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    {turns, directions} = parse_lines(lines)
    turn_indefinitely(turns, directions, "AAA", "ZZZ")
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines) do
    {turns, directions} = parse_lines(lines)

    starts =
      directions
      |> Map.keys()
      |> Enum.filter(fn x -> String.ends_with?(x, "A") end)

    turn_indefinitely_on_multiple_paths(turns, directions, starts)
  end

  @spec parse_lines([String.t()]) :: {[turn()], direction_map()}
  defp parse_lines(lines) do
    [turns, _ | rest] = lines
    turns = String.graphemes(turns) |> Enum.map(&String.to_atom/1)

    directions =
      Enum.reduce(rest, %{}, fn line, acc ->
        [start, left_right] = String.split(line, " = ")
        [left, right] = left_right |> String.trim("(") |> String.trim(")") |> String.split(", ")
        Map.put(acc, start, {left, right})
      end)

    {turns, directions}
  end

  @spec follow_turn(String.t(), turn(), direction_map()) :: String.t()
  defp follow_turn(start, turn, directions) do
    directions
    |> Map.get(start)
    |> case do
      {left, _} when turn == :L -> left
      {_, right} when turn == :R -> right
    end
  end

  @spec turn_indefinitely([turn()], direction_map(), String.t(), String.t()) :: integer()
  defp turn_indefinitely(turns, directions, start_position, end_position) do
    try do
      turns
      |> Stream.cycle()
      |> Stream.with_index()
      |> Enum.reduce(start_position, fn {turn, index}, acc ->
        case follow_turn(acc, turn, directions) do
          ^end_position -> throw({:exit, index + 1})
          position -> position
        end
      end)
    catch
      {:exit, exit_counter} -> exit_counter
    end
  end

  @spec compute_cycle(String.t(), [turn()], direction_map()) :: integer()
  defp compute_cycle(start, turns, directions) do
    try do
      turns
      |> Stream.cycle()
      |> Stream.with_index()
      |> Enum.reduce(start, fn {turn, index}, position ->
        new_position = follow_turn(position, turn, directions)

        if String.ends_with?(new_position, "Z") do
          throw({:exit, index + 1})
        else
          follow_turn(position, turn, directions)
        end
      end)
    catch
      {:exit, exit_counter} -> exit_counter
    end
  end

  @spec lcm(integer(), integer()) :: integer()
  defp lcm(a, b) do
    trunc(a * b / Integer.gcd(a, b))
  end

  @spec turn_indefinitely_on_multiple_paths([turn()], direction_map(), [String.t()]) :: integer()
  defp turn_indefinitely_on_multiple_paths(turns, directions, starts) do
    starts
    |> Enum.map(fn x -> compute_cycle(x, turns, directions) end)
    |> Enum.reduce(1, &lcm/2)
  end
end
