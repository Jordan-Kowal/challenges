defmodule AdventOfCode.DayTask do
  @callback part1(data :: String.t()) :: any()
  @callback part2(data :: String.t(), p1_result :: any()) :: any()
  @callback parse_input(input :: String.t()) :: any()

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
        {time, _} =
          :timer.tc(fn ->
            IO.puts("Solving #{module_name()}")
            input = log_func_call(fn -> read_input() end, :read_input)
            data = log_func_call(fn -> parse_input(input) end, :parse_input)
            p1_result = log_func_call(fn -> part1(data) end, :part1, true)
            _p2_result = log_func_call(fn -> part2(data, p1_result) end, :part2, true)
          end)

        IO.puts("Total time: #{time / 1_000_000}s")
      end

      @impl AdventOfCode.DayTask
      @doc """
      Parses the input for the day.
      """
      @spec parse_input(String.t()) :: any()
      def parse_input(input), do: input

      @impl AdventOfCode.DayTask
      @doc """
      Solves part 1 of the puzzle for the day.
      """
      @spec part1(String.t()) :: any()
      def part1(_data), do: :ok

      @impl AdventOfCode.DayTask
      @doc """
      Solves part 2 of the puzzle for the day.
      """
      @spec part2(String.t(), any()) :: any()
      def part2(_data, _p1_result), do: :ok

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
        input
      end

      # Times a function call and logs the result.
      @spec log_func_call((any() -> any()), String.t(), boolean()) :: integer()
      defp log_func_call(func, name, print_output \\ false)

      defp log_func_call(func, name, print_output) do
        {micro_seconds, output} = :timer.tc(func)
        seconds = micro_seconds / 1_000_000

        if print_output do
          IO.puts("#{name} -> #{inspect(output)} (#{seconds}s)")
        else
          IO.puts("#{name} (#{seconds}s)")
        end

        output
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
