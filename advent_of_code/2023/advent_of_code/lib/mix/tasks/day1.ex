defmodule Mix.Tasks.Day1 do
  use AdventOfCode.DayTask

  @first_and_last_digits_regex ~r/^\D*(\d).*?(\d)\D*$/
  @first_digit_regex ~r/(\d)/
  @word_and_digit_regex ~r/(one|two|three|four|five|six|seven|eight|nine|\d)/i

  @impl AdventOfCode.DayTask
  def solve_p1(lines) do
    lines
    |> Enum.filter(fn line -> line != "" end)
    |> Enum.map(fn line ->
      case Regex.run(@first_and_last_digits_regex, line) do
        [_, first, last] ->
          String.to_integer("#{first}#{last}")

        _ ->
          [_, first] = Regex.run(@first_digit_regex, line)
          String.to_integer("#{first}#{first}")
      end
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
        |> String.replace(~r/one/, "o1ne")
        |> String.replace(~r/two/, "t2wo")
        |> String.replace(~r/three/, "t3hree")
        |> String.replace(~r/four/, "f4our")
        |> String.replace(~r/five/, "f5ive")
        |> String.replace(~r/six/, "s6ix")
        |> String.replace(~r/seven/, "s7even")
        |> String.replace(~r/eight/, "e8ight")
        |> String.replace(~r/nine/, "n9ine")

      matches = Regex.scan(@word_and_digit_regex, line)
      [first, _] = hd(matches)
      [last, _] = List.last(matches)
      String.to_integer("#{first}#{last}")
    end)
    |> Enum.sum()
  end
end
