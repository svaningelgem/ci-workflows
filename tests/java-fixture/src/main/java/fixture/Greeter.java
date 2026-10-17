package fixture;

public final class Greeter {
    private Greeter() {
    }

    public static String greet(String name) {
        return name.isBlank() ? "Hello!" : "Hello, " + name + "!";
    }
}
