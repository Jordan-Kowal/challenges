defmodule Mix.Tasks.Benchmark do
  @moduledoc """
  Runs all days and prints the execution time of each day/part.
  """

  use Mix.Task

  alias Mix.Tasks.{Day1, Day2}

  @modules [Day1, Day2]
  @padding 10
  @iterations 1

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

    read_times = Enum.map(results, fn {x, _, _} -> x end)
    p1_times = Enum.map(results, fn {_, x, _} -> x end)
    p2_times = Enum.map(results, fn {_, _, x} -> x end)

    count = length(read_times)
    read_first = hd(read_times)
    p1_avg = Enum.sum(p1_times) / count
    p2_avg = Enum.sum(p2_times) / count

    """
    #{String.pad_trailing(module.module_name(), @padding)}
    #{String.pad_trailing("#{inspect(Float.round(p1_avg, 5))}s", @padding)}
    #{String.pad_trailing("#{inspect(Float.round(p2_avg, 5))}s", @padding)}
    """
    |> String.replace("\n", "")
    |> IO.puts()
  end
end
