/**
 * Slack App Home Calendar
 * ──────────────────────────
 * Generates an interactive calendar for date selection in App Home
 */

export function generateAppHomeCalendar(): Record<string, unknown> {
  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();

  // Generate current month calendar
  const monthName = new Date(currentYear, currentMonth, 1).toLocaleString(
    'default',
    { month: 'long', year: 'numeric' }
  );

  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  const blocks: Array<Record<string, unknown>> = [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: '📅 Panchangam Calculator',
        emoji: true,
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: 'Select a date to calculate the Panchangam. Click any date below.',
      },
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*${monthName}*`,
      },
    },
  ];

  // Create calendar grid
  const calendarDays: Array<Record<string, unknown>> = [];

  // Empty slots before first day
  for (let i = 0; i < firstDay; i++) {
    calendarDays.push({
      type: 'button',
      text: {
        type: 'plain_text',
        text: ' ',
        emoji: true,
      },
      action_id: 'empty',
      disabled: true,
    });
  }

  // Days of month
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = formatDate(currentYear, currentMonth, day);
    const isToday = day === today.getDate();

    calendarDays.push({
      type: 'button',
      text: {
        type: 'plain_text',
        text: String(day),
        emoji: true,
      },
      value: dateStr,
      action_id: `date_${dateStr}`,
      style: isToday ? 'primary' : 'default',
    });
  }

  // Empty slots after last day
  const totalCells = calendarDays.length;
  const rowsNeeded = Math.ceil(totalCells / 7);
  const totalSlots = rowsNeeded * 7;
  for (let i = totalCells; i < totalSlots; i++) {
    calendarDays.push({
      type: 'button',
      text: {
        type: 'plain_text',
        text: ' ',
        emoji: true,
      },
      action_id: 'empty',
      disabled: true,
    });
  }

  // Group days into weeks
  for (let i = 0; i < calendarDays.length; i += 7) {
    const weekDays = calendarDays.slice(i, i + 7);
    blocks.push({
      type: 'actions',
      elements: weekDays,
      block_id: `week_${Math.floor(i / 7)}`,
    });
  }

  blocks.push({
    type: 'divider',
  });

  blocks.push({
    type: 'section',
    text: {
      type: 'mrkdwn',
      text: '💡 Click any date above to calculate the Panchangam for that day.',
    },
  });

  return {
    type: 'home',
    blocks,
  };
}

function formatDate(year: number, month: number, day: number): string {
  const m = String(month + 1).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${year}-${m}-${d}`;
}

export function extractDateFromAction(action_id: string): string | null {
  if (action_id.startsWith('date_')) {
    return action_id.substring(5); // Remove 'date_' prefix
  }
  return null;
}
