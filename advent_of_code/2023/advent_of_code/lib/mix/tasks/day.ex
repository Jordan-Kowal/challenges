defmodule Mix.Tasks.Day do
  @moduledoc """
  Copy-paste this file to create a new day task.
  """

  use AdventOfCode.DayTask

  @impl AdventOfCode.DayTask
  def solve_p1(_data) do
    :ok
  end

  @impl AdventOfCode.DayTask
  def solve_p2(_data, _p1_result) do
    :ok
  end

  @impl AdventOfCode.DayTask
  def parse_input_p1(input) do
    input
  end

  @impl AdventOfCode.DayTask
  def parse_input_p2(input) do
    parse_input_p1(input)
  end
end
