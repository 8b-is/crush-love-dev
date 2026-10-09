// Command jcharm — the Charm-native front door to jcode's UI.
//
// One small Bubble Tea / Lip Gloss / Glamour panel that composes the three
// Charm surfaces with jcode's UI:
//
//	jcode          — the UI (the rich Rust TUI)
//	crush          — the engine (Charm's agent CLI; the crush-love-dev runtime)
//	charm CLI tools — gum / glow / vhs / mods, detected and used when present
//
// This is the Rust↔Go seam made concrete: jcode's UI is Rust and cannot link
// the Go charmbracelet libraries, so Charm builds the entry (this panel) and
// jcode keeps the UI. `crush-love-dev --jcode` runs it.
//
//	jcharm                 the lane report (no TUI)
//	jcharm ui [args...]    exec jcode — the UI, with Charm armed around it
//	jcharm engine <text>   run crush headless, render the reply with Glamour
//	jcharm tui             the interactive Charm panel
package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/glamour"
	"github.com/charmbracelet/lipgloss"
)

// ── the lane: jcode's UI, the engine, and the charm CLI tools ───────────────

type surface struct {
	name string
	role string
	bin  string
}

func surfaces() []surface {
	return []surface{
		{"jcode", "the UI — the rich Rust TUI", "jcode"},
		{"crush", "the engine — Charm's agent CLI", "crush"},
		{"gum", "charm CLI — glamorous shell prompts", "gum"},
		{"glow", "charm CLI — terminal markdown", "glow"},
		{"vhs", "charm CLI — record the terminal", "vhs"},
		{"mods", "charm CLI — the LLM in the shell", "mods"},
	}
}

func found(bin string) string {
	if p, err := exec.LookPath(bin); err == nil {
		return p
	}
	return ""
}

var (
	pink  = lipgloss.Color("#FF4D9D")
	blue  = lipgloss.Color("#A6C8FF")
	dim   = lipgloss.Color("#4C5570")
	gold  = lipgloss.Color("#E8B05C")
	title = lipgloss.NewStyle().Foreground(pink).Bold(true)
	role  = lipgloss.NewStyle().Foreground(blue)
	off   = lipgloss.NewStyle().Foreground(dim)
	mark  = lipgloss.NewStyle().Foreground(gold)
	box   = lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).
		BorderForeground(dim).Padding(0, 2)
)

// report renders the lane as a Lip Gloss panel — the non-interactive view.
func report() string {
	var b strings.Builder
	b.WriteString(title.Render("jcode ♥ Charm") + off.Render(" · the beta lane") + "\n")
	b.WriteString(off.Render("jcode's UI, wrapped in Charm's existing capabilities") + "\n\n")
	for _, s := range surfaces() {
		if p := found(s.bin); p != "" {
			b.WriteString(mark.Render("✓ ") + role.Render(fmt.Sprintf("%-6s", s.name)) +
				off.Render(" "+s.role) + "\n")
			_ = p
		} else {
			b.WriteString(off.Render("· ") + off.Render(fmt.Sprintf("%-6s", s.name)) +
				off.Render(" "+s.role+"  (not on PATH)") + "\n")
		}
	}
	b.WriteString("\n" + off.Render("install the missing charm tools: brew install gum glow vhs mods"))
	return box.Render(b.String())
}

// renderMarkdown sends text through Glamour — Charm's markdown capability,
// applied to a reply (e.g. the engine's).
func renderMarkdown(md string) string {
	r, err := glamour.NewTermRenderer(glamour.WithAutoStyle(), glamour.WithWordWrap(100))
	if err != nil {
		return md
	}
	out, err := r.Render(md)
	if err != nil {
		return md
	}
	return out
}

// runHeadless asks the engine (crush) and renders its reply with Glamour.
func runHeadless(prompt string) error {
	crush := found("crush")
	if crush == "" {
		return fmt.Errorf("crush not on PATH — the engine is not installed")
	}
	cmd := exec.Command(crush, "run", "--quiet", prompt)
	cmd.Stderr = os.Stderr
	out, err := cmd.Output()
	if err != nil {
		return err
	}
	fmt.Println(renderMarkdown(strings.TrimSpace(string(out))))
	return nil
}

// ── the interactive panel (Bubble Tea) ─────────────────────────────────────

type action struct {
	label string
	exec  string
}

type model struct {
	actions []action
	cursor  int
}

func newModel() model {
	a := []action{}
	if found("jcode") != "" {
		a = append(a, action{"launch jcode — the UI", "jcode"})
	}
	if found("crush") != "" {
		a = append(a, action{"open crush — the engine", "crush"})
	}
	if found("glow") != "" {
		a = append(a, action{"glow README — Charm markdown", "glow"})
	}
	a = append(a, action{"show the lane report", ""})
	return model{actions: a}
}

func (m model) Init() tea.Cmd { return nil }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	k, ok := msg.(tea.KeyMsg)
	if !ok {
		return m, nil
	}
	switch k.String() {
	case "q", "esc", "ctrl+c":
		return m, tea.Quit
	case "up", "k":
		if m.cursor > 0 {
			m.cursor--
		}
	case "down", "j":
		if m.cursor < len(m.actions)-1 {
			m.cursor++
		}
	case "enter":
		sel := m.actions[m.cursor]
		if sel.exec == "" {
			return m, tea.Quit
		}
		if sel.exec == "glow" {
			return m, tea.ExecProcess(exec.Command("glow", "README.md"), func(error) tea.Msg { return nil })
		}
		return m, tea.ExecProcess(exec.Command(sel.exec), func(error) tea.Msg { return nil })
	}
	return m, nil
}

func (m model) View() string {
	var b strings.Builder
	b.WriteString(title.Render("jcode ♥ Charm") + off.Render(" · the beta lane") + "\n\n")
	for i, a := range m.actions {
		if i == m.cursor {
			b.WriteString(mark.Render("▶ "+a.label) + "\n")
		} else {
			b.WriteString(off.Render("  "+a.label) + "\n")
		}
	}
	b.WriteString("\n" + off.Render("↑/↓ move · enter select · q quit"))
	return box.Render(b.String())
}

// ── entry ──────────────────────────────────────────────────────────────────

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		fmt.Println(report())
		return
	}
	switch args[0] {
	case "ui":
		bin := found("jcode")
		if bin == "" {
			fmt.Fprintln(os.Stderr, "jcharm: jcode not on PATH")
			os.Exit(1)
		}
		cmd := exec.Command(bin, args[1:]...)
		cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
		if err := cmd.Run(); err != nil {
			os.Exit(1)
		}
	case "engine":
		if len(args) < 2 {
			fmt.Fprintln(os.Stderr, "jcharm: engine needs a prompt")
			os.Exit(2)
		}
		if err := runHeadless(strings.Join(args[1:], " ")); err != nil {
			fmt.Fprintln(os.Stderr, "jcharm:", err)
			os.Exit(1)
		}
	case "tui":
		if _, err := tea.NewProgram(newModel()).Run(); err != nil {
			fmt.Fprintln(os.Stderr, "jcharm:", err)
			os.Exit(1)
		}
	case "-h", "--help":
		fmt.Println(report())
	default:
		fmt.Fprintln(os.Stderr, "jcharm: unknown command "+args[0]+" (ui|engine|tui)")
		os.Exit(2)
	}
}
