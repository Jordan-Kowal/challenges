defmodule AdventOfCode.DayTask do
  @callback solve_p1(lines :: [String.t()]) :: any()
  @callback solve_p2(lines :: [String.t()], p1_result :: any()) :: any()

  defmacro __using__(_opts) do
    quote do
      use Mix.Task

      @behaviour AdventOfCode.DayTask

      @impl Mix.Task
      @doc """
      Runs the task to solve the puzzle for the day.
      """
      @spec run(binary()) :: any()
      def run(_) do
        {micro_seconds, p1_result} =
          :timer.tc(fn ->
            read_input()
            |> solve_p1()
          end)

        seconds = Float.round(micro_seconds / 1_000_000, 3)
        IO.puts("(#{seconds}s) P1 -> #{inspect(p1_result)}")

        {micro_seconds, p2_result} =
          :timer.tc(fn ->
            read_input()
            |> solve_p2(p1_result)
          end)

        seconds = Float.round(micro_seconds / 1_000_000, 3)
        IO.puts("(#{seconds}s) P2 -> #{inspect(p2_result)}")
      end

      # Reads the input file for the day.
      @spec read_input() :: String.t()
      defp read_input() do
        project_root = File.cwd!()

        filename =
          module_name()
          |> String.downcase()
          |> (&(&1 <> ".txt")).()

        filepath = Path.join([project_root, "data", filename])
        {:ok, input} = File.read(filepath)
        String.split(input, "\n")
      end

      # Returns the last part of the module name.
      @spec module_name() :: String.t()
      defp module_name() do
        __MODULE__
        |> to_string()
        |> String.split(".")
        |> List.last()
      end
    end
  end
end
