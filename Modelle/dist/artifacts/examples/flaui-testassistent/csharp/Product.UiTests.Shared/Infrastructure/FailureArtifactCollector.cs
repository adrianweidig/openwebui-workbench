using System.Text.Json;
using FlaUI.Core.AutomationElements;
using Product.UiTests.Shared.Diagnostics;

namespace Product.UiTests.Shared.Infrastructure;

public static class FailureArtifactCollector
{
    public static void Collect(Window? window, ArtifactPaths paths, string testName, Exception? exception)
    {
        var metadata = new
        {
            TestName = testName,
            CreatedUtc = DateTime.UtcNow,
            Machine = Environment.MachineName,
            User = Environment.UserName,
            Exception = exception?.ToString()
        };

        File.WriteAllText(
            Path.Combine(paths.Metadata, "metadata.json"),
            JsonSerializer.Serialize(metadata, new JsonSerializerOptions { WriteIndented = true }));

        if (window is not null)
        {
            try
            {
                var capture = window.Capture();
                capture.ToFile(Path.Combine(paths.Screenshots, "failure-window.png"));
                UiaTreeDumper.Dump(window, Path.Combine(paths.UiaDumps, "uia-tree.xml"));
            }
            catch (Exception artifactException)
            {
                File.WriteAllText(Path.Combine(paths.Logs, "artifact-error.txt"), artifactException.ToString());
            }
        }
    }
}
