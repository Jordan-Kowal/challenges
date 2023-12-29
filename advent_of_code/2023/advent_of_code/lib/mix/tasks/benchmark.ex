defmodule Mix.Tasks.Benchmark do
  @moduledoc """
  Runs all days and prints the execution time of each day/part.
  """

  use Mix.Task

  @modules [
    Mix.Tasks.Day1,
    Mix.Tasks.Day2,
    Mix.Tasks.Day3,
    Mix.Tasks.Day4,
    Mix.Tasks.Day5
    # Mix.Tasks.Day6,
    # Mix.Tasks.Day7,
    # Mix.Tasks.Day8,
    # Mix.Tasks.Day9,
    # Mix.Tasks.Day10,
    # Mix.Tasks.Day11,
    # Mix.Tasks.Day12,
    # Mix.Tasks.Day13,
    # Mix.Tasks.Day14,
    # Mix.Tasks.Day15,
    # Mix.Tasks.Day16,
    # Mix.Tasks.Day17,
    # Mix.Tasks.Day18,
    # Mix.Tasks.Day19,
    # Mix.Tasks.Day20,
    # Mix.Tasks.Day21,
    # Mix.Tasks.Day22,
    # Mix.Tasks.Day23,
    # Mix.Tasks.Day24,
    # Mix.Tasks.Day25
  ]
  @padding 10
  @iterations 1

  @impl Mix.Task
  def run(_) do
    IO.puts("Running benchmark...")

    """
    #{String.pad_trailing("Day", @padding)}
    #{String.pad_trailing("P1", @padding)}
    #{String.pad_trailing("P2", @padding)}
    """
    |> String.replace("\n", "")
    |> IO.puts()

    Enum.map(@modules, &run_benchmark/1)
  end

  defp run_benchmark(module) do
    results = Enum.map(1..@iterations, fn _ -> module.run(["--silent"]) end)

    p1_times = Enum.map(results, fn {x, _} -> x end)
    p2_times = Enum.map(results, fn {_, x} -> x end)

    p1_avg = Enum.sum(p1_times) / length(p1_times)
    p2_avg = Enum.sum(p2_times) / length(p2_times)

    """
    #{String.pad_trailing(module.module_name(), @padding)}
    #{String.pad_trailing("#{inspect(Float.round(p1_avg, 5))}s", @padding)}
    #{String.pad_trailing("#{inspect(Float.round(p2_avg, 5))}s", @padding)}
    """
    |> String.replace("\n", "")
    |> IO.puts()
  end
end
