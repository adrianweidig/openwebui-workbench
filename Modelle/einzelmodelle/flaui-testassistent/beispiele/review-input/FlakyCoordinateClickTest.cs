using FlaUI.Core.Input;
using NUnit.Framework;

namespace Product.UiTests.Uia3.BadExamples;

[TestFixture]
public sealed class FlakyCoordinateClickTest
{
    [Test]
    public void Bad_Coordinate_Click_Example()
    {
        // Negativbeispiel: Dieser Test ist absichtlich schlecht.
        // Er klickt Koordinaten, wartet statisch und prüft Text über Fullscreen-Pixelvergleich.
        Mouse.Click(742, 513);
        Thread.Sleep(5000);

        Assert.Pass("Dieser Test ist als Review-Beispiel gedacht, nicht als Zielmuster.");
    }
}
