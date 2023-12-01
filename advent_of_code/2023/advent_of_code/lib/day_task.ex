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
      def run(opts) do
        [silent: silent] = parse_options(opts)
        # Read input
        {micro_seconds, lines} = :timer.tc(fn -> read_input() end)
        read_seconds = micro_seconds / 1_000_000

        unless silent do
          IO.puts("(#{Float.round(read_seconds, 3)}s) Read input")
        end

        # P1
        {micro_seconds, p1_result} = :timer.tc(fn -> solve_p1(lines) end)
        p1_seconds = micro_seconds / 1_000_000

        unless silent do
          IO.puts("(#{Float.round(p1_seconds, 3)}s) P1 -> #{inspect(p1_result)}")
        end

        # P2
        {micro_seconds, p2_result} = :timer.tc(fn -> solve_p2(lines, p1_result) end)
        p2_seconds = micro_seconds / 1_000_000

        unless silent do
          IO.puts("(#{Float.round(p2_seconds, 3)}s) P2 -> #{inspect(p2_result)}")
        end

        {read_seconds, p1_seconds, p2_seconds}
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

      @doc """
      Returns the last part of the module name.
      """
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
