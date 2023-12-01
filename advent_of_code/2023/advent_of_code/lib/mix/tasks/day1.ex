defmodule Mix.Tasks.Day1 do
  use AdventOfCode.DayTask

  defoverridable part1: 1, part2: 2, parse_input: 1

  @impl AdventOfCode.DayTask
  def part1(_data) do
    :ko
  end

  @impl AdventOfCode.DayTask
  def part2(_data, _p1_result) do
    :ko
  end

  @impl AdventOfCode.DayTask
  def parse_input(input) do
    input
  end
end
