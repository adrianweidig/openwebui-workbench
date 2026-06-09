using System.Net;
using System.Text.Json;
using ApiContract.Xunit.Tests.Models;
using ApiContract.Xunit.Tests.Support;
using Xunit;

namespace ApiContract.Xunit.Tests.Tests;

public sealed class TodoApiContractTests : IClassFixture<ApiClientFixture>
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);
    private readonly ApiClientFixture _fixture;

    public TodoApiContractTests(ApiClientFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task GetTodoById_ReturnsExpectedContractShape()
    {
        using var response = await _fixture.Client.GetAsync("/api/todos/42", TestContext.Current.CancellationToken);

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        await using var responseStream = await response.Content.ReadAsStreamAsync(TestContext.Current.CancellationToken);
        var todo = await JsonSerializer.DeserializeAsync<TodoItem>(
            responseStream,
            JsonOptions,
            TestContext.Current.CancellationToken);

        Assert.NotNull(todo);
        Assert.Equal(42, todo!.Id);
        Assert.False(string.IsNullOrWhiteSpace(todo.Title));
    }

    [Fact]
    public async Task GetUnknownTodo_ReturnsNotFoundWithoutServerError()
    {
        using var response = await _fixture.Client.GetAsync("/api/todos/999999", TestContext.Current.CancellationToken);

        // The exact error body may vary, but the API must not turn a valid unknown ID into a 5xx defect.
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
