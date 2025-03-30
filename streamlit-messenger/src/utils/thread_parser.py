import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class RaceThread:
    filename: str
    date: datetime
    racecourse: str
    race_number: int
    full_path: str
    
    @property
    def display_name(self) -> str:
        return f"{self.date.strftime('%Y-%m-%d')} {self.racecourse} {self.race_number}R"
        
def parse_filename(filename: str) -> tuple[datetime, str, int]:
    """Parse race details from filename"""
    # Example: 20250330_中京_11_202507020611_20250330_151632_pred_v8.csv
    parts = filename.split('_')
    date = datetime.strptime(parts[0], '%Y%m%d')
    racecourse = parts[1]
    race_number = int(parts[2])
    return date, racecourse, race_number

def get_race_threads(data_dir: str) -> List[RaceThread]:
    """Get all race threads from the data directory"""
    threads = []
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv'):
            continue
            
        try:
            date, racecourse, race_number = parse_filename(filename)
            threads.append(RaceThread(
                filename=filename,
                date=date,
                racecourse=racecourse,
                race_number=race_number,
                full_path=os.path.join(data_dir, filename)
            ))
        except (ValueError, IndexError):
            # Skip files that don't match the expected format
            continue
            
    # Sort threads by date and race number
    return sorted(threads, key=lambda t: (t.date, t.race_number))