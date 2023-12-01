defmodule Mix.Tasks.Day1 do
  use AdventOfCode.DayTask

  @first_and_last_digits_regex ~r/^\D*(\d).*?(\d)\D*$/
  @first_digit_regex ~r/(\d)/

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    lines
    |> Enum.filter(fn line -> line != "" end)
    |> Enum.map(fn line ->
      {first, last} = match_first_and_last_digits(line)
      String.to_integer("#{first}#{last}")
    end)
    |> Enum.sum()
  end

  @impl AdventOfCode.DayTask
  def solve_p2(lines, _p1_result) do
    lines
    |> Enum.filter(fn line -> line != "" end)
    |> Enum.map(fn line ->
      line =
        line
        |> String.replace("one", "o1ne")
        |> String.replace("two", "t2wo")
        |> String.replace("three", "t3hree")
        |> String.replace("four", "f4our")
        |> String.replace("five", "f5ive")
        |> String.replace("six", "s6ix")
        |> String.replace("seven", "s7even")
        |> String.replace("eight", "e8ight")
        |> String.replace("nine", "n9ine")

      {first, last} = match_first_and_last_digits(line)
      String.to_integer("#{first}#{last}")
    end)
    |> Enum.sum()
  end

  # Returns the first and last digits of the line.
  @spec match_first_and_last_digits(String.t()) :: {String.t(), String.t()}
  defp match_first_and_last_digits(line) do
    case Regex.run(@first_and_last_digits_regex, line) do
      [_, first, last] ->
        {first, last}

      _ ->
        [_, first] = Regex.run(@first_digit_regex, line)
        {first, first}
    end
  end
end
