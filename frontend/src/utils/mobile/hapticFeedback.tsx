/**
 * Haptic Feedback Utility for Mobile Devices
 * Provides various haptic feedback patterns for enhanced mobile UX
 */

import React from 'react';

export enum HapticFeedbackType {
  LIGHT = 'light',
  MEDIUM = 'medium',
  HEAVY = 'heavy',
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  SELECTION = 'selection',
  IMPACT = 'impact',
}

interface HapticPattern {
  vibrate?: number | number[];
  intensity?: number;
  duration?: number;
}

class HapticFeedbackManager {
  private isSupported: boolean;
  private patterns: Record<HapticFeedbackType, HapticPattern>;

  constructor() {
    this.isSupported = 'vibrate' in navigator;
    this.patterns = {
      [HapticFeedbackType.LIGHT]: { vibrate: 10 },
      [HapticFeedbackType.MEDIUM]: { vibrate: 25 },
      [HapticFeedbackType.HEAVY]: { vibrate: 50 },
      [HapticFeedbackType.SUCCESS]: { vibrate: [20, 10, 20] },
      [HapticFeedbackType.ERROR]: { vibrate: [50, 30, 50, 30, 50] },
      [HapticFeedbackType.WARNING]: { vibrate: [30, 10, 30] },
      [HapticFeedbackType.SELECTION]: { vibrate: 15 },
      [HapticFeedbackType.IMPACT]: { vibrate: 40 },
    };
  }

  /**
   * Trigger haptic feedback with specified type
   */
  public trigger(type: HapticFeedbackType, force: boolean = false): boolean {
    if (!this.isSupported && !force) {
      return false;
    }

    const pattern = this.patterns[type];
    if (!pattern.vibrate) {
      return false;
    }

    try {
      navigator.vibrate(pattern.vibrate);
      return true;
    } catch (error) {
      console.warn('Haptic feedback failed:', error);
      return false;
    }
  }

  /**
   * Trigger custom haptic pattern
   */
  public triggerCustom(pattern: number | number[]): boolean {
    if (!this.isSupported) {
      return false;
    }

    try {
      navigator.vibrate(pattern);
      return true;
    } catch (error) {
      console.warn('Custom haptic feedback failed:', error);
      return false;
    }
  }

  /**
   * Stop all haptic feedback
   */
  public stop(): void {
    if (this.isSupported) {
      navigator.vibrate(0);
    }
  }

  /**
   * Check if haptic feedback is supported
   */
  public isHapticSupported(): boolean {
    return this.isSupported;
  }

  /**
   * Set custom pattern for a feedback type
   */
  public setCustomPattern(type: HapticFeedbackType, pattern: HapticPattern): void {
    this.patterns[type] = pattern;
  }
}

// Singleton instance
export const hapticFeedback = new HapticFeedbackManager();

/**
 * React Hook for Haptic Feedback
 */
export const useHapticFeedback = () => {
  const trigger = (type: HapticFeedbackType, force?: boolean) => {
    return hapticFeedback.trigger(type, force);
  };

  const triggerCustom = (pattern: number | number[]) => {
    return hapticFeedback.triggerCustom(pattern);
  };

  const stop = () => {
    hapticFeedback.stop();
  };

  const isSupported = hapticFeedback.isHapticSupported();

  return {
    trigger,
    triggerCustom,
    stop,
    isSupported,
    HapticFeedbackType,
  };
};

/**
 * Higher-order component for adding haptic feedback to any component
 */
export interface WithHapticFeedbackProps {
  hapticType?: HapticFeedbackType;
  hapticOnPress?: boolean;
  hapticOnSuccess?: boolean;
  hapticOnError?: boolean;
  disableHaptic?: boolean;
}

export const withHapticFeedback = <P extends object>(
  WrappedComponent: React.ComponentType<P>
) => {
  const HapticWrappedComponent: React.FC<P & WithHapticFeedbackProps> = ({
    hapticType = HapticFeedbackType.SELECTION,
    hapticOnPress = true,
    hapticOnSuccess = false,
    hapticOnError = false,
    disableHaptic = false,
    ...props
  }) => {
    const { trigger } = useHapticFeedback();

    const enhancedProps = {
      ...props,
      onPress: (...args: any[]) => {
        if (hapticOnPress && !disableHaptic) {
          trigger(hapticType);
        }
        if ((props as any).onPress) {
          (props as any).onPress(...args);
        }
      },
      onSuccess: (...args: any[]) => {
        if (hapticOnSuccess && !disableHaptic) {
          trigger(HapticFeedbackType.SUCCESS);
        }
        if ((props as any).onSuccess) {
          (props as any).onSuccess(...args);
        }
      },
      onError: (...args: any[]) => {
        if (hapticOnError && !disableHaptic) {
          trigger(HapticFeedbackType.ERROR);
        }
        if ((props as any).onError) {
          (props as any).onError(...args);
        }
      },
    } as P;

    return React.createElement(WrappedComponent, enhancedProps);
  };

  HapticWrappedComponent.displayName = `withHapticFeedback(${WrappedComponent.displayName || WrappedComponent.name})`;

  return HapticWrappedComponent;
};

export default hapticFeedback;