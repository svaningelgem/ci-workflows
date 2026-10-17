package fixture;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class GreeterTest {
    @Test
    void greetsByName() {
        assertEquals("Hello, Ada!", Greeter.greet("Ada"));
    }

    @Test
    void greetsNobody() {
        assertEquals("Hello!", Greeter.greet(" "));
    }
}
