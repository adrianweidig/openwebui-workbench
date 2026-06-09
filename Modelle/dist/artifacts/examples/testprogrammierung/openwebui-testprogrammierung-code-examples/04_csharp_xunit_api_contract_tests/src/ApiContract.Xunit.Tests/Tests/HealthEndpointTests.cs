using System.Net;
using ApiContract.Xunit.Tests.Support;
using Xunit;

namespace ApiContract.Xunit.Tests.Tests;

public sealed class HealthEndpointTests : IClassFixture<ApiClientFixture>
{
    private readonly ApiClientFixture _fixture;

    public HealthEndpointTests(ApiClientFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task GetHealth_ReturnsSuccessAndJsonContentType()
    {
        using var response = await _fixture.Client.GetAsync("/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("application/json", response.Content.Headers.ContentType?.MediaType);
    }
}
