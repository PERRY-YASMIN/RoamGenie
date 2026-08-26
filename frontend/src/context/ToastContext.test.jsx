import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ToastContainer from "../components/ToastContainer";
import { ToastProvider, useToast } from "./ToastContext";

function TestConsumer() {
  const { showToast, success, error, warning, info } = useToast();
  return (
    <div>
      <button onClick={() => showToast("General message", "info", 0)}>Show Info</button>
      <button onClick={() => success("Trip saved successfully!", 0)}>Show Success</button>
      <button onClick={() => error("Failed to save trip", 0)}>Show Error</button>
      <button onClick={() => warning("Budget deficit detected", 0)}>Show Warning</button>
      <button onClick={() => success("Timed toast", 100)}>Show Timed</button>
    </div>
  );
}

describe("Toast Notification System (M6)", () => {
  it("renders toast notifications of various types", () => {
    render(
      <ToastProvider>
        <TestConsumer />
        <ToastContainer />
      </ToastProvider>
    );

    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByText("Trip saved successfully!")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Show Error"));
    expect(screen.getByText("Failed to save trip")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Show Warning"));
    expect(screen.getByText("Budget deficit detected")).toBeInTheDocument();
  });

  it("allows manual dismissal of toasts", () => {
    render(
      <ToastProvider>
        <TestConsumer />
        <ToastContainer />
      </ToastProvider>
    );

    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByText("Trip saved successfully!")).toBeInTheDocument();

    const dismissBtns = screen.getAllByLabelText("Dismiss notification");
    fireEvent.click(dismissBtns[0]);

    expect(screen.queryByText("Trip saved successfully!")).not.toBeInTheDocument();
  });

  it("auto-dismisses toasts after the specified duration", async () => {
    vi.useFakeTimers();

    render(
      <ToastProvider>
        <TestConsumer />
        <ToastContainer />
      </ToastProvider>
    );

    fireEvent.click(screen.getByText("Show Timed"));
    expect(screen.getByText("Timed toast")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(150);
    });

    expect(screen.queryByText("Timed toast")).not.toBeInTheDocument();
    vi.useRealTimers();
  });
});
