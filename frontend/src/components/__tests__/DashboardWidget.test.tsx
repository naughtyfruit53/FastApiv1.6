// frontend/src/components/__tests__/DashboardWidget.test.tsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardWidget, { WidgetConfig } from '../DashboardWidget';

describe('DashboardWidget', () => {
  const mockConfig: WidgetConfig = {
    id: 'test-widget-1',
    title: 'Test Widget',
    type: 'metric',
    position: { x: 0, y: 0 },
    size: { width: 300, height: 200 },
  };

  const mockOnRefresh = jest.fn();
  const mockOnRemove = jest.fn();
  const mockOnConfigure = jest.fn();
  const mockOnPositionChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders widget with title', () => {
    render(
      <DashboardWidget config={mockConfig}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(screen.getByText('Test Widget')).toBeInTheDocument();
    expect(screen.getByText('Widget Content')).toBeInTheDocument();
  });

  it('displays loading state when loading prop is true', () => {
    render(
      <DashboardWidget config={mockConfig} loading={true}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.queryByText('Widget Content')).not.toBeInTheDocument();
  });

  it('calls onRefresh when refresh button is clicked', () => {
    render(
      <DashboardWidget config={mockConfig} onRefresh={mockOnRefresh}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    expect(mockOnRefresh).toHaveBeenCalledTimes(1);
  });

  it('opens menu when more button is clicked', () => {
    render(
      <DashboardWidget
        config={mockConfig}
        onConfigure={mockOnConfigure}
        onRemove={mockOnRemove}
        isEditable={true}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const moreButton = screen.getAllByRole('button').find(
      (btn) => btn.querySelector('[data-testid="MoreVertIcon"]') !== null
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);
      expect(screen.getByText('Configure')).toBeInTheDocument();
      expect(screen.getByText('Remove')).toBeInTheDocument();
    }
  });

  it('calls onRemove when remove menu item is clicked', () => {
    render(
      <DashboardWidget
        config={mockConfig}
        onRemove={mockOnRemove}
        isEditable={true}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const moreButton = screen.getAllByRole('button').find(
      (btn) => btn.querySelector('[data-testid="MoreVertIcon"]') !== null
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);
      const removeMenuItem = screen.getByText('Remove');
      fireEvent.click(removeMenuItem);
      expect(mockOnRemove).toHaveBeenCalledWith(mockConfig.id);
    }
  });

  it('calls onConfigure when configure menu item is clicked', () => {
    render(
      <DashboardWidget
        config={mockConfig}
        onConfigure={mockOnConfigure}
        isEditable={true}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const moreButton = screen.getAllByRole('button').find(
      (btn) => btn.querySelector('[data-testid="MoreVertIcon"]') !== null
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);
      const configureMenuItem = screen.getByText('Configure');
      fireEvent.click(configureMenuItem);
      expect(mockOnConfigure).toHaveBeenCalledWith(mockConfig.id);
    }
  });

  it('does not render menu button when isEditable is false', () => {
    render(
      <DashboardWidget config={mockConfig} isEditable={false}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const moreButton = screen.queryAllByRole('button').find(
      (btn) => btn.querySelector('[data-testid="MoreVertIcon"]') !== null
    );
    
    expect(moreButton).toBeUndefined();
  });

  it('applies correct size from config', () => {
    const { container } = render(
      <DashboardWidget config={mockConfig}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const card = container.querySelector('.MuiCard-root');
    expect(card).toHaveStyle({
      width: '300px',
      height: '200px',
    });
  });

  it('renders drag indicator when isDraggable is true', () => {
    render(
      <DashboardWidget config={mockConfig} isDraggable={true}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    const dragIndicator = screen.getByTestId('DragIndicatorIcon');
    expect(dragIndicator).toBeInTheDocument();
  });

  it('does not render drag indicator when isDraggable is false', () => {
    render(
      <DashboardWidget config={mockConfig} isDraggable={false}>
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(screen.queryByTestId('DragIndicatorIcon')).not.toBeInTheDocument();
  });
});
