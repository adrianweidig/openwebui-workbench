using System.Text.Json.Serialization;

namespace ApiContract.Xunit.Tests.Models;

public sealed record TodoItem(
    [property: JsonPropertyName("id")] int Id,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("completed")] bool Completed);
