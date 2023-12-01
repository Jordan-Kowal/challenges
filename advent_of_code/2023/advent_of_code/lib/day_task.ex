defmodule AdventOfCode.DayTask do
  @callback parse_input_p1(input :: String.t()) :: any()
  @callback parse_input_p2(input :: String.t()) :: any()
  @callback solve_p1(data :: String.t()) :: any()
  @callback solve_p2(data :: String.t(), p1_result :: any()) :: any()

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
            |> parse_input_p1()
            |> solve_p1()
          end)

        seconds = Float.round(micro_seconds / 1_000_000, 4)
        IO.puts("(#{seconds}s) P1 -> #{inspect(p1_result)}")

        {micro_seconds, p2_result} =
          :timer.tc(fn ->
            read_input()
            |> parse_input_p2()
            |> solve_p2(p1_result)
          end)

        seconds = Float.round(micro_seconds / 1_000_000, 4)
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
        input
      end

      # Times a function call and logs the result.
      @spec log_func_call((any() -> any()), String.t(), boolean()) :: integer()
      defp log_func_call(func, name, print_output \\ false)

      defp log_func_call(func, name, print_output) do
        {micro_seconds, output} = :timer.tc(func)
        seconds = micro_seconds / 1_000_000

        if print_output do
          IO.puts("(#{seconds}s) #{name} -> #{inspect(output)}")
        else
          IO.puts("(#{seconds}s) #{name}")
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
