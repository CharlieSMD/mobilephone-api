export const formatSpec = (value?: string | number, suffix?: string): string => {
  if (value === undefined || value === null || value === '') return 'Not specified';
  return suffix ? `${value}${suffix}` : `${value}`;
};


