defmodule AdventOfCode.DayTask do
  @moduledoc """
  Basic Mix.Task template for an Advent of Code day.
  Defines both a behaviour and a macro.
  """

  @callback solve_p1(lines :: [String.t()]) :: any()
  @callback solve_p2(lines :: [String.t()]) :: any()

  defmacro __using__(_opts) do
    quote do
      use Mix.Task

      @behaviour AdventOfCode.DayTask

      @impl Mix.Task
      @doc "Runs the task to solve the puzzle for the day."
      @spec run([binary()]) :: {float(), float()}
      def run(opts) do
        [silent: silent] = parse_options(opts)

        lines = read_input()
        {p1_time, p1_result} = :timer.tc(fn -> solve_p1(lines) end)
        {p2_time, p2_result} = :timer.tc(fn -> solve_p2(lines) end)
        p1_seconds = p1_time / 1_000_000
        p2_seconds = p2_time / 1_000_000

        unless silent do
          IO.puts("(#{Float.round(p1_seconds, 5)}s) P1 -> #{inspect(p1_result)}")
          IO.puts("(#{Float.round(p2_seconds, 5)}s) P2 -> #{inspect(p2_result)}")
        end

        {p1_seconds, p2_seconds}
      end

      # Reads the input file for the day.
      @spec read_input() :: [String.t()]
      defp read_input() do
        project_root = File.cwd!()

        filename =
          module_name()
          |> String.downcase()
          |> (&(&1 <> ".txt")).()

        lines =
          Path.join([project_root, "data", filename])
          |> File.read!()
          |> String.split("\n")

        if Enum.at(lines, -1) == "" do
          List.delete_at(lines, -1)
        else
          lines
        end
      end

      @doc "Returns the last part of the module name."
      @spec module_name() :: String.t()
      def module_name() do
        __MODULE__
        |> to_string()
        |> String.split(".")
        |> List.last()
      end

      defp parse_options(args) do
        {opts, _} = OptionParser.parse!(args, strict: [silent: :boolean])
        [silent: opts[:silent] || false]
      end
    end
  end
end
